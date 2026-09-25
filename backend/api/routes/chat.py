import time
import re
import base64
import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends

from schemas.chat import ChatCreateSchema, RenameSchema, ChatRequest, ChatResponse
from dependencies import get_memory, get_retrieval_service
from schemas.retrieval.retrieval_request import RetrievalRequest
from services.retrieval.retrieval_service import RetrievalService
from services.evaluation_service import calculate_rag_metrics
from services.ingestion_service import IngestionService
from engines.generation.generation_engine import GenerationEngine
from settings import settings

router = APIRouter()

def classify_query(query: str, attachments: list) -> str:
    query_lower = query.lower().strip()
    query_clean = re.sub(r'[^\w\s]', '', query_lower).strip()

    # 1. Unsafe Request
    unsafe_keywords = ["exploit", "hack", "bypass security", "illegal", "crack password"]
    if any(kw in query_clean for kw in unsafe_keywords):
        return "UNSAFE_REQUEST"

    # 2. Token Optimisation checks (Acknowledgements)
    acknowledgements = {"thanks", "thank you", "okay", "ok", "sure", "done", "perfect", "got it", "understood", "yes", "no", "confirm", "cancel"}
    if query_clean in acknowledgements:
        return "CONVERSATIONAL"

    # 3. Greeting
    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening", "hola", "greetings", "yo"}
    if query_clean in greetings or query_clean.startswith("hey "):
        return "GREETING"

    # 4. Small Talk
    small_talk = {
        "how are you", "what can you do", "who are you", "tell me about yourself",
        "whats your name", "what is your name", "who developed you", "who built you",
        "who created you", "tell me about you"
    }
    if query_clean in small_talk:
        return "SMALL_TALK"

    # 5. Identity Questions
    identity = ["do you remember me", "who am i", "what's my name", "what is my name", "my name is", "i am", "do you know me", "do u know me"]
    if any(id_q in query_clean for id_q in identity):
        return "IDENTITY_QUESTIONS"

    # 6. Conversation Follow-up
    follow_ups = ["explain again", "continue", "more details", "simplify this", "summarise above", "tell me more"]
    if any(f_u in query_clean for f_u in follow_ups):
        return "CONVERSATION_FOLLOW_UP"

    # 7. Web Search
    web_keywords = ["search the web", "browse", "internet", "google search", "current weather", "latest news"]
    if any(wk in query_lower for wk in web_keywords):
        return "WEB_SEARCH"

    # 8. Analytics Request
    analytics = ["chart", "plot", "eda", "statistics", "kpi", "graph", "dataframe analytics"]
    if any(an in query_lower for an in analytics):
        return "ANALYTICS_REQUEST"

    # 9. Database Query
    db_keywords = ["select", "sql", "query database", "database table", "from table", "join", "group by", "order by", "where", "insert into", "create table"]
    if any(db in query_lower for db in db_keywords):
        return "DATABASE_QUERY"

    # 10. Coding Request
    coding = [
        "code", "python", "sql", "function", "class", "method", "import", "def", "script",
        "error", "exception", "debug", "compile", "run", "syntax", "js", "html", "css",
        "binary search", "algorithm", "sort", "linked list", "tree", "array", "recursion",
        "write a python", "write python", "write code", "implement", "program", "developer"
    ]
    if any(cd in query_lower for cd in coding) or re.search(r'[{}\[\]();<>+=/*]', query):
        return "CODING_REQUEST"

    # 11. Document Question (text files, PDFs, CSVs)
    if attachments and any(
        a.get('textContent') or
        (a.get('dataUrl') and (a.get('type') == 'application/pdf' or a.get('name', '').lower().endswith(('.pdf', '.docx', '.xlsx', '.csv', '.txt', '.pptx'))))
        for a in attachments
    ):
        return "DOCUMENT_QUESTION"

    # 12. Visual Analysis (Image snapshots only)
    if attachments and any(
        a.get('type', '').startswith('image/') or
        a.get('name', '').lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff'))
        for a in attachments
    ):
        return "VISUAL_ANALYSIS"

    # 13. Company Knowledge
    company_keywords = ["policy", "leave", "onboarding", "hr", "benefits", "ABC Software", "office", "holiday"]
    if any(ck in query_lower for ck in company_keywords):
        return "COMPANY_KNOWLEDGE"

    if len(query.split()) == 0:
        return "AMBIGUOUS_REQUEST"

    if len(query.split()) < 5:
        return "SIMPLE_KNOWLEDGE"

    return "TECHNICAL_KNOWLEDGE"

def ocr_base64_image(data_url: str) -> str:
    try:
        import numpy as np
        import cv2
        from services.document_intelligence import DocumentIntelligence

        if "," in data_url:
            header, base64_data = data_url.split(",", 1)
        else:
            base64_data = data_url

        image_bytes = base64.b64decode(base64_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is not None:
            # Preserve resolution for high-DPI screenshots (up to 2500px)
            max_dim = 2500
            h, w = img.shape[:2]
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

            reader = DocumentIntelligence.get_reader()
            results = reader.readtext(img)
            extracted = " ".join(t for _, t, _ in results)

            # If standard OCR extracted minimal text, try contrast enhancement (CLAHE for dark mode/low contrast screenshots)
            if len(extracted.strip()) < 15:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
                enhanced = clahe.apply(gray)
                res_enh = reader.readtext(enhanced)
                extracted_enh = " ".join(t for _, t, _ in res_enh)
                if len(extracted_enh.strip()) > len(extracted.strip()):
                    extracted = extracted_enh

            if extracted.strip():
                return f"[Extracted Image/Snapshot Text & Visual Code]:\n{extracted.strip()}"
    except Exception as e:
        print(f"Error performing OCR on image attachment: {e}")
    return ""

def extract_pdf_from_base64(data_url: str) -> str:
    try:
        import pypdf
        import io

        if "," in data_url:
            header, base64_data = data_url.split(",", 1)
        else:
            base64_data = data_url

        pdf_bytes = base64.b64decode(base64_data)
        pdf_file = io.BytesIO(pdf_bytes)

        reader = pypdf.PdfReader(pdf_file)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        print(f"Error extracting PDF text from attachment: {e}")
    return ""


async def extract_attachment_content(attach: dict) -> str:
    """
    Extract text content from any frontend attachment (OCR for images/snapshots,
    DocumentExtractor for PDF, DOCX, XLSX, PPTX, CSV, TXT, code files).
    """
    name = attach.get('name', 'attachment')
    text = attach.get('textContent')
    if text and text.strip():
        return text.strip()

    data_url = attach.get('dataUrl')
    if not data_url:
        return ""

    # Image snapshots / uploaded image files
    is_img = attach.get('type', '').startswith('image/') or name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif'))
    if is_img:
        import asyncio
        return await asyncio.to_thread(ocr_base64_image, data_url)

    # Non-image files (PDF, DOCX, XLSX, PPTX, CSV, TXT, etc.)
    try:
        header, base64_data = data_url.split(",", 1) if "," in data_url else ("", data_url)
        file_bytes = base64.b64decode(base64_data)

        import io
        from fastapi import UploadFile
        from services.document_intelligence import DocumentIntelligence

        mock_file = UploadFile(
            filename=name,
            file=io.BytesIO(file_bytes)
        )

        extracted = await DocumentIntelligence.extract_text(mock_file)
        if extracted and extracted.strip():
            return extracted.strip()
    except Exception as e:
        print(f"Error in DocumentIntelligence extraction for {name}: {e}")

    # Fallback to PyPDF if PDF
    if name.lower().endswith('.pdf') or attach.get('type') == 'application/pdf':
        return extract_pdf_from_base64(data_url)

    return ""


# --- Conversations CRUD ---

@router.get("")
async def list_chats(memory = Depends(get_memory)):
    return memory.list_conversations()

'''@router.post("")
async def create_chat(data: ChatCreateSchema, memory = Depends(get_memory)):
    from uuid import uuid4
    chat_id = f"chat-{int(time.time() * 1000)}-{uuid4().hex[:6]}"
    print(f"[CHAT CREATE] id={chat_id} title={data.title}")
    return memory.create_conversation(chat_id, data.title, data.model)'''

@router.post("")
async def create_chat(data: ChatCreateSchema, memory = Depends(get_memory)):
    from uuid import uuid4

    chat_id = f"chat-{int(time.time() * 1000)}-{uuid4().hex[:6]}"

    print(f"[CREATE CHAT] chat_id={chat_id}")

    result = memory.create_conversation(
        chat_id,
        data.title,
        data.model
    )

    print(f"[CREATE CHAT RESULT] {result}")

    return result

@router.put("/{chat_id}")
async def rename_chat(chat_id: str, data: RenameSchema, memory = Depends(get_memory)):
    success = memory.update_conversation(chat_id, title=data.title, model=data.model)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"status": "success"}

@router.delete("/{chat_id}")
async def delete_chat(chat_id: str, memory = Depends(get_memory)):
    success = memory.delete_conversation(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"status": "success"}

# --- Messages CRUD & Orchestration Pipeline ---

@router.get("/{chat_id}/messages")
async def get_messages(chat_id: str, memory = Depends(get_memory)):
    return memory.get_messages(chat_id)

@router.delete("/{chat_id}/messages/truncate/{msg_id}")
async def truncate_chat_messages(chat_id: str, msg_id: str, memory = Depends(get_memory)):
    success = memory.truncate_messages(chat_id, msg_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "success"}

@router.post("/{chat_id}/messages")
async def post_message(
    chat_id: str,
    data: ChatRequest,
    memory = Depends(get_memory),
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    start_time = time.time()

    print(f"[CHAT MESSAGE] looking for {chat_id}")

    chat = memory.get_conversation(chat_id)

    print(f"[CHAT FOUND] {chat is not None}")

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    history = memory.get_messages(chat_id)
    query = data.text

    # Pipeline trace — collects each processing step for the frontend panel
    pipeline_trace = []
    # 1. Query Classification (Rule-based to prevent semantic latency/errors)
    query_clean = re.sub(r'[^\w\s]', '', query.lower()).strip()

    is_greeting = query_clean in [
        "hi", "hello", "hey", "good morning", "good evening", "good afternoon",
        "whats up", "howdy", "greetings", "thanks", "thank you", "okay", "ok",
        "got it", "understood", "great", "awesome", "perfect"
    ]

    # Robust help and capability request checking
    help_keywords = [
        "how can you help", "what can you do", "what are your capabilities",
        "what do you do", "who are you", "how to use", "what is this app",
        "what is this assistant", "what topics do you cover", "what topics are covered",
        "what is this knowledge base about", "what is this kb about",
        "what documentation do you have", "what documents do you have",
        "what files do you have"
    ]
    query_clean_no_spaces = query_clean.replace(" ", "")
    is_help_request = any(kw in query_clean for kw in help_keywords) or \
                      "howcanyouhelp" in query_clean_no_spaces or \
                      "whatcanyoudo" in query_clean_no_spaces or \
                      "whatisthiskb" in query_clean_no_spaces or \
                      "whatareyourcapabilities" in query_clean_no_spaces

    if not query.strip():
        detected_intent = "GREETING"
    elif data.attachments:
        detected_intent = "KNOWLEDGE_QUERY"
    elif is_help_request:
        detected_intent = "HELP_REQUEST"
    elif is_greeting:
        detected_intent = "GREETING"
    else:
        detected_intent = "KNOWLEDGE_QUERY"

    print(f"[RAG Router] Classified Intent: {detected_intent}")
    pipeline_trace.append({
        "step": 1,
        "label": "Query Classification",
        "detail": f"Intent detected: {detected_intent}",
        "status": "done"
    })

    # --- ROUTE 1: DYNAMIC HELP REQUEST ---
    if detected_intent == "HELP_REQUEST":
        # Resolve UI system prompt
        system_instruction = data.system_prompt
        if not system_instruction:
            sp_file = settings.PROJECT_ROOT / "backend" / "data" / "system_prompt.txt"
            if sp_file.exists():
                try:
                    with open(sp_file, "r", encoding="utf-8") as f:
                        system_instruction = f.read()
                except Exception:
                    pass
        if not system_instruction:
            system_instruction = os.getenv("SYSTEM_PROMPT") or settings.SYSTEM_PROMPT

        # List all files loaded in the registry to build dynamic capability context
        docs = memory.list_documents()
        doc_names = [d["name"] for d in docs] if docs else []
        kb_context = f"Indexed Documents in the Knowledge Base:\n" + ("\n".join(f"- {name}" for name in doc_names) if doc_names else "- No documents indexed yet.")

        messages = [{"role": "system", "content": system_instruction}]
        for msg in history[-6:]:
            role = "user" if msg['sender'] == 'user' else "assistant"
            messages.append({"role": role, "content": msg['text']})

        user_content = f"Context: This is a capability query. Here are the active files in the knowledge base:\n{kb_context}\n\nUser Question: {query}"
        messages.append({"role": "user", "content": user_content})

        from engines.generation.generation_engine import GenerationEngine
        generation_engine = GenerationEngine()

        try:
            response_text = await generation_engine.generate(
                model=data.model,
                messages=messages,
                temperature=0.4,
            )
            # Dynamic strip for prompt leakage
            leakage_phrases = [
                "I am a strict Enterprise Knowledge Base Assistant.",
                "Based on retrieved chunks.",
                "According to compressed context.",
                "Based on internal instructions.",
                "Based on the provided information",
                "According to retrieved documents",
                "According to the provided documents",
                "Based on the retrieved context",
                "Based on the context provided",
                "Based on the retrieved documents"
            ]
            for phrase in leakage_phrases:
                response_text = re.sub(re.escape(phrase) + r"\,?\s*", "", response_text, flags=re.IGNORECASE)
            response_text = response_text.strip()
            if response_text and response_text[0].islower():
                response_text = response_text[0].upper() + response_text[1:]
        except Exception as e:
            response_text = f"I am a knowledge base assistant. I can help answer questions using the documents loaded in the database: {', '.join(doc_names) if doc_names else 'No documents loaded yet.'}"

        memory.add_message(conversation_id=chat_id, sender="user", text=query, attachments=data.attachments)
        assistant_msg = memory.add_message(
            conversation_id=chat_id,
            sender="assistant",
            text=response_text,
            citations=[]
        )

        # Log decision path
        print("\n" + "="*50)
        print("--- STRICT RAG DEBUG LOG ---")
        print(f"User Question: '{query}'")
        print(f"Scope Detection Result: 'HELP_REQUEST'")
        print(f"Intent Type: 'HELP_REQUEST'")
        print(f"Retrieved Chunk Count: 0")
        print(f"Top Score: 0.0000")
        print(f"Average Score: 0.0000")
        print(f"Relevant Chunk Count: 0")
        print(f"Answerability Result: N/A")
        print(f"LLM Invoked (Yes/No): Yes")
        print(f"Final Response Path: Help Request -> Dynamic LLM-generated response based on KB registry")
        print("="*50 + "\n")

        return assistant_msg

    # --- ROUTE 2: GREETING & SMALL_TALK INTENT ---
    if detected_intent == "GREETING":
        if query_clean in ["thanks", "thank you", "great", "awesome", "perfect"]:
            response_text = "You're welcome! Let me know if you need anything else."
        elif query_clean in ["okay", "ok", "got it", "understood"]:
            response_text = "Understood. Feel free to ask any other questions."
        else:
            response_text = (
                "Hello! I am your knowledge base assistant.\n\n"
                "I can help answer questions using information available in the current knowledge base."
            )

        memory.add_message(conversation_id=chat_id, sender="user", text=query, attachments=data.attachments)
        assistant_msg = memory.add_message(
            conversation_id=chat_id,
            sender="assistant",
            text=response_text,
            citations=[]
        )

        # Log decision path
        print("\n" + "="*50)
        print("--- STRICT RAG DEBUG LOG ---")
        print(f"User Question: '{query}'")
        print(f"Scope Detection Result: 'GREETING'")
        print(f"Intent Type: 'GREETING'")
        print(f"Retrieved Chunk Count: 0")
        print(f"Top Score: 0.0000")
        print(f"Average Score: 0.0000")
        print(f"Relevant Chunk Count: 0")
        print(f"Answerability Result: N/A")
        print(f"LLM Invoked (Yes/No): No")
        print(f"Final Response Path: Greeting / Small Talk -> Predefined Response")
        print("="*50 + "\n")

        return assistant_msg

    # --- ROUTE 3: KNOWLEDGE_QUERY INTENT (Retrieval + Validation + Generation) ---
    url_pattern = r'https?://[^\s>]+'
    urls = re.findall(url_pattern, query)
    url_attached_parts = []
    citations = []

    if urls:
        from services.ingestion.web_loader import WebLoader
        for url in urls:
            clean_url = url.rstrip('.,;()[]{}')
            try:
                print(f"[Chat Pipeline] Live fetching URL in real-time: {clean_url}")
                loader = WebLoader(clean_url, timeout=12)
                web_data = loader.fetch_and_clean()
                page_title = web_data.get("title", clean_url)
                page_text = web_data.get("text", "")

                if page_text:
                    url_attached_parts.append(
                        f"=== Live Webpage Content: {page_title} ({clean_url}) ===\n"
                        f"{page_text[:8000]}\n"
                        f"========================================================"
                    )
                    citations.append({
                        "id": f"url-{time.time()}",
                        "name": f"🌐 {page_title}",
                        "source": f"{page_title} ({clean_url})",
                        "score": 1.0,
                        "snippet": page_text[:300] + "..."
                    })

                    # Queue background vector store indexing
                    import asyncio
                    asyncio.create_task(IngestionService.ingest_url(clean_url, memory))
            except Exception as web_err:
                print(f"[Chat Pipeline] Error live browsing URL {clean_url}: {web_err}")

    # Save User Message
    user_msg = memory.add_message(
        conversation_id=chat_id,
        sender="user",
        text=query,
        attachments=data.attachments
    )

    # Extract Frontend Attachments
    attachment_parts = []
    attachment_parts.extend(url_attached_parts)

    for attach in data.attachments:
        extracted_text = await extract_attachment_content(attach)
        if extracted_text and extracted_text.strip():
            attachment_parts.append(
                f"=== Attached File: {attach.get('name', 'attachment')} ===\n"
                f"{extracted_text.strip()}\n"
                f"====================================="
            )
            citations.append({
                "id": attach.get('id', str(time.time())),
                "name": attach.get('name', 'Attached Document'),
                "source": attach.get('name', 'Attached Document') + " (Direct Attachment)",
                "score": 1.0,
                "snippet": extracted_text.strip()[:300] + "..."
            })

            # Auto-ingest into Knowledge Base
            try:
                import asyncio
                asyncio.create_task(
                    IngestionService.ingest_pasted_content(
                        title=attach.get('name', 'Attached Document'),
                        content=extracted_text.strip(),
                        memory=memory
                    )
                )
            except Exception as ing_err:
                print(f"Warning: Could not auto-ingest attachment '{attach.get('name')}': {ing_err}")

    retrieved_context_str = ""
    has_attachments = len(attachment_parts) > 0
    should_retrieve = True

    rewritten_query = query
    if history:
        try:
            history_str = ""
            for msg in history[-5:]:
                sender = "User" if msg['sender'] == 'user' else "Assistant"
                history_str += f"{sender}: {msg['text']}\n"

            rewrite_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a search query optimizer. Analyze the conversation history and the latest user query, "
                        "and generate a standalone search query optimized for vector database retrieval.\n"
                        "Instructions:\n"
                        "1. Identify the core user intent, goal, and the active conversational topic from the history.\n"
                        "2. Resolve any relative references, pronouns, continuation requests, or short follow-ups (e.g. 'next', 'roadmap', 'more details', 'guide me') by expanding them with the relevant topic context (e.g. 'n8n nodes' or 'Hypergene data integration').\n"
                        "3. Keep the output as a concise search query (combining key terms and search phrases) to retrieve high-quality matches from the knowledge base.\n"
                        "4. Output ONLY the optimized query text. Do not add explanations, conversational filler, or introductory notes."
                    )
                },
                {
                    "role": "user",
                    "content": f"Conversation History:\n{history_str}\nFollow-up Query: {query}\n\nOptimized Search Query:"
                }
            ]
            from engines.generation.generation_engine import GenerationEngine

            print("[DEBUG] Creating GenerationEngine")
            generation_engine = GenerationEngine()

            model_name = data.model
            print(f"[DEBUG] About to call LLM with model={model_name}")

            rewritten = await generation_engine.generate(
                model=model_name,
                messages=rewrite_messages,
                temperature=0.0
            )

            print("[DEBUG] LLM call completed successfully")
            rewritten_query = rewritten.strip()
            print(f"[Query Rewriter] Rewrote '{query}' -> '{rewritten_query}'")
        except Exception as e:
            print(f"[Query Rewriter] Error rewriting query: {e}")
    num_docs = 0
    best_score = 0.0
    average_score = 0.0
    relevant_chunks = []
    try:
        embedding_model = (
            data.settings.get("embedding_model")
            or data.settings.get("embeddingModel")
        )

        embedding_api_key = (
            data.settings.get("embedding_api_key")
            or data.settings.get("embeddingApiKey")
        )

        req = RetrievalRequest(
            query=rewritten_query,
            top_k=data.settings.get("topK", 3),
            filters={},
            embedding_model=embedding_model,
            embedding_api_key=embedding_api_key,
        )
        pipeline_trace.append({
            "step": 2,
            "label": "Query Rewriting",
            "detail": f"Rewrote query to: '{rewritten_query}'",
            "status": "done"
        })

        # Embedding preview
        try:
            import os as _os
            from services.embedding_service import EmbeddingService
            _active_emb = (
                data.settings.get("embedding_model")
                or data.settings.get("embeddingModel")
                or _os.getenv("ACTIVE_EMBEDDING_MODEL")
            )

            _embedding_key = (
                data.settings.get("embedding_api_key")
                or data.settings.get("embeddingApiKey")
            )

            _emb_preview = EmbeddingService(
                model_name=_active_emb,
                api_key=_embedding_key,
            ).generate_embedding(query)
            emb_dims = len(_emb_preview) if _emb_preview else 0
            pipeline_trace.append({
                "step": 3,
                "label": "Embedding Generation",
                "detail": f"Query converted to {emb_dims}-dim vector embedding.",
                "status": "done"
            })
        except Exception:
            pass

        pipeline_trace.append({
            "step": 4,
            "label": "Semantic & Keyword Search",
            "detail": f"Running dense + sparse retrieval...",
            "status": "running"
        })
        response_retrieval, context_str = await retrieval_service.retrieve(req)
        retrieved_context_str = context_str
        num_docs = len(response_retrieval.documents)
        pipeline_trace[-1]["detail"] = f"Retrieved {num_docs} document chunk(s)"
        pipeline_trace[-1]["status"] = "done"

        # RAG Threshold Variables
        import os
        min_score = float(os.getenv("RETRIEVAL_MIN_SCORE", os.getenv("RETRIEVER_SIMILARITY", str(settings.RETRIEVAL_MIN_SCORE))))
        min_chunks = int(os.getenv("MIN_REQUIRED_CHUNKS", str(settings.MIN_REQUIRED_CHUNKS)))

        best_score = 0.0
        average_score = 0.0
        if response_retrieval.documents:
            best_score = max(doc.score for doc in response_retrieval.documents)
            average_score = sum(doc.score for doc in response_retrieval.documents) / len(response_retrieval.documents)

        relevant_chunks = [
            doc for doc in response_retrieval.documents
            if doc.score >= min_score
        ]

        # Step 6: If retrieval returns weak results (or no docs), attempt query expansion / refinement
        if (not response_retrieval.documents or best_score < min_score) and not has_attachments:
            print(f"[Retrieval Refinement] Initial search returned weak results (Best Score: {best_score:.4f} < Min Score: {min_score}). Attempting query expansion...")
            try:
                refine_prompt = [
                    {
                        "role": "system",
                        "content": (
                            "You are a search query expansion assistant. Given a user query and a conversation history, "
                            "generate exactly 3 alternative, simplified search phrases to find relevant documentation in a vector database.\n"
                            "- Focus on alternate keywords, synonyms, and variations of the core topic.\n"
                            "- Do not explain, return ONLY a valid JSON array of 3 strings."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"User Query: {query}\nHistory:\n{history_str if history else 'None'}\n\nJSON Output:"
                    }
                ]
                print("[Retrieval Refinement] Generating alternate queries with LLM...")
                t_ref_start = time.time()
                refine_res = await generation_engine.generate(
                    model=data.model,
                    messages=refine_prompt,
                    temperature=0.0
                )
                print(f"[Retrieval Refinement] LLM call completed in {time.time() - t_ref_start:.2f} seconds. Result: '{refine_res}'")

                # Parse JSON array of alternative queries
                alt_queries = []
                try:
                    clean_res = refine_res.strip()
                    if clean_res.startswith("```"):
                        clean_res = clean_res.split("```")[1]
                        if clean_res.startswith("json"):
                            clean_res = clean_res[4:]
                    alt_queries = json.loads(clean_res.strip())
                except Exception as parse_err:
                    print(f"[Retrieval Refinement] JSON parse error: {parse_err}. Extracting strings.")
                    alt_queries = re.findall(r'"([^"]+)"', refine_res)

                print(f"[Retrieval Refinement] Generated alternate queries: {alt_queries}")

                # Fetch docs for each query and combine
                combined_docs = list(response_retrieval.documents)
                seen_ids = {doc.id for doc in combined_docs}

                import asyncio
                from services.retrieval.strategies.hybrid_strategy import HybridStrategy
                hybrid_strategy = HybridStrategy()
                tasks = [
                    hybrid_strategy.retrieve(RetrievalRequest(
                        query=alt_q,
                        top_k=data.settings.get('topK', 3),
                        filters={},
                        embedding_model=embedding_model,
                        embedding_api_key=embedding_api_key,
                    ))
                    for alt_q in alt_queries[:3]
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception) or not res:
                        continue
                    alt_resp = res[0]
                    for doc in alt_resp.documents:
                        if doc.id not in seen_ids:
                            combined_docs.append(doc)
                            seen_ids.add(doc.id)

                # Re-sort combined documents by score descending
                combined_docs.sort(key=lambda d: d.score, reverse=True)
                response_retrieval.documents = combined_docs

                # Update best score and relevant chunks
                if response_retrieval.documents:
                    best_score = max(doc.score for doc in response_retrieval.documents)
                    average_score = sum(doc.score for doc in response_retrieval.documents) / len(response_retrieval.documents)
                relevant_chunks = [
                    doc for doc in response_retrieval.documents
                    if doc.score >= min_score
                ]
                # Rebuild context string
                from services.retrieval.context_builder import ContextBuilder
                retrieved_context_str = ContextBuilder.build(response_retrieval.documents)
                num_docs = len(response_retrieval.documents)
                print(f"[Retrieval Refinement] Completed refinement. Combined Docs Count: {num_docs}, New Best Score: {best_score:.4f}, Relevant: {len(relevant_chunks)}")
            except Exception as ref_err:
                print(f"[Retrieval Refinement] Error during expansion: {ref_err}")

        # Post-retrieval validation check: if no relevant context can be found after expansion, fall back
        if (not response_retrieval.documents or len(relevant_chunks) == 0) and not has_attachments:
            fallback_msg = "I could not find information about this in the knowledge base."
            return memory.add_message(
                conversation_id=chat_id,
                sender="assistant",
                text=fallback_msg,
                citations=[]
            )

        # Citations cap at 3
        MAX_CITATIONS = 3
        SNIPPET_MAX_CHARS = 150
        for doc in response_retrieval.documents[:MAX_CITATIONS]:
            raw_snippet = doc.text or ""
            display_snippet = raw_snippet[:SNIPPET_MAX_CHARS] + ("..." if len(raw_snippet) > SNIPPET_MAX_CHARS else "")
            citations.append({
                "id": doc.id,
                "name": doc.source or "Database Vector Store",
                "source": doc.source or "Database Vector Store",
                "score": doc.score,
                "snippet": display_snippet
            })

        pipeline_trace.append({
            "step": 5,
            "label": "Context Assembly",
            "detail": "Context assembled successfully",
            "status": "done"
        })

    except Exception as e:
        print(f"[Retrieval Error] Failed to retrieve context: {e}")

    # --- LLM Answer Generation using System Prompt (Precedence: request -> flat-file -> env var -> config default) ---
    system_instruction = data.system_prompt
    if not system_instruction:
        sp_file = settings.PROJECT_ROOT / "backend" / "data" / "system_prompt.txt"
        if sp_file.exists():
            try:
                with open(sp_file, "r", encoding="utf-8") as f:
                    system_instruction = f.read()
            except Exception:
                pass
    if not system_instruction:
        system_instruction = os.getenv("SYSTEM_PROMPT") or settings.SYSTEM_PROMPT

    messages = [{"role": "system", "content": system_instruction}]
    for msg in history[-6:]:
        role = "user" if msg['sender'] == 'user' else "assistant"
        messages.append({"role": role, "content": msg['text']})

    from services.generation.prompt_builder import PromptBuilder
    prompt_builder = PromptBuilder()

    if has_attachments:
        combined_context = "\n\n".join(attachment_parts)
        user_content = prompt_builder.build(query=query, context=combined_context, has_attachments=True)
    else:
        user_content = prompt_builder.build(query=query, context=retrieved_context_str, has_attachments=False)

    messages.append({"role": "user", "content": user_content})

    from engines.generation.generation_engine import GenerationEngine
    generation_engine = GenerationEngine()

    response_text = ""
    is_technical_error = False
    llm_step_num = len(pipeline_trace) + 1
    pipeline_trace.append({
        "step": llm_step_num,
        "label": "Sending to LLM",
        "detail": f"Sending assembled context + query to model: {data.model}",
        "status": "running"
    })

    try:
        print(f"[CHAT ROUTE] About to call LLM")
        print(f"[CHAT ROUTE] Model = {data.model}")
        print(f"[CHAT ROUTE] Messages Count = {len(messages)}")

        response_text = await generation_engine.generate(
            model=data.model,
            messages=messages,
            temperature=data.settings.get("temperature", 0.2),
        )

        print(f"[CHAT ROUTE] Response Length = {len(response_text)}")
        pipeline_trace[-1]["status"] = "done"
        pipeline_trace[-1]["detail"] = f"LLM ({data.model}) generated response successfully"

        # Clean up any prompt leakage or filler phrases from the output text dynamically
        leakage_phrases = [
            "I am a strict Enterprise Knowledge Base Assistant.",
            "Based on retrieved chunks.",
            "According to compressed context.",
            "Based on internal instructions.",
            "Based on the provided information",
            "According to retrieved documents",
            "According to the provided documents",
            "Based on the retrieved context",
            "Based on the context provided",
            "Based on the retrieved documents"
        ]
        for phrase in leakage_phrases:
            response_text = re.sub(re.escape(phrase) + r"\,?\s*", "", response_text, flags=re.IGNORECASE)

        response_text = response_text.strip()
        if response_text and response_text[0].islower():
            response_text = response_text[0].upper() + response_text[1:]

        # Log decision path
        print("\n" + "="*50)
        print("--- STRICT RAG DEBUG LOG ---")
        print(f"User Question: '{query}'")
        print(f"Scope Detection Result: 'KNOWLEDGE_QUERY'")
        print(f"Intent Type: 'KNOWLEDGE_QUERY'")
        print(f"Retrieved Chunk Count: {num_docs}")
        print(f"Top Score: {best_score:.4f}")
        print(f"Average Score: {average_score:.4f}")
        print(f"Relevant Chunk Count: {len(relevant_chunks)}")
        print(f"Answerability Result: YES")
        print(f"LLM Invoked (Yes/No): Yes")
        print(f"Final Decision Path: KNOWLEDGE_QUERY -> Validated -> Answerability YES -> Synthesized Response")
        print("="*50 + "\n")

    except Exception as e:
        is_technical_error = True
        pipeline_trace[-1]["status"] = "error"
        pipeline_trace[-1]["detail"] = f"LLM error: {e}"
        import traceback
        print(f"[LLM Error] Generating response failed: {e}")
        traceback.print_exc()
        response_text = (
            f"⚠️ Error generating response from LLM (`{data.model}`): {str(e)}\n\n"
            "Failed to generate a response from the selected LLM. Please check the selected model and provider/API configuration in Settings."
        )

    # 10b. Generate context-aware follow-up suggestions (concurrent, non-blocking)
    suggestions = []
    try:
        def _get_clean_topic(text: str, max_len: int = 50) -> str:
            cleaned = text.strip()
            if len(cleaned) <= max_len:
                return cleaned
            words = cleaned[:max_len].rsplit(" ", 1)
            return words[0] if words[0] else cleaned[:max_len]

        clean_topic = _get_clean_topic(query, 50)

        suggestion_messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert AI assistant. Based on the user prompt and assistant response, "
                    "generate exactly 3 complete, natural, highly relevant follow-up questions or actions "
                    "the user might want to ask next to explore the topic deeper.\n"
                    "- Every suggestion MUST be a complete, well-formatted sentence or question.\n"
                    "- Do NOT truncate sentences or cut off mid-word.\n"
                    "- Include 1 web search action formatted as 'Search Google: [topic]'\n"
                    "- Output ONLY a valid JSON array of 3 strings.\n"
                    "Example: [\"What are the practical applications of deep learning?\", \"Search Google: deep learning algorithms latest updates 2026\", \"How do neural networks compare to traditional models?\"]"
                )
            },
            {
                "role": "user",
                "content": f"User Prompt: {query}\nAssistant Response Context: {response_text[:800]}\n\nGenerate 3 complete follow-up suggestions as a JSON array."
            }
        ]
        generation_engine = GenerationEngine()

        suggestion_raw = await generation_engine.generate(
            model=data.model,
            messages=suggestion_messages,
            temperature=0.6,
        )

        # Parse JSON safely
        import re as _re
        json_match = _re.search(r'\[.*?\]', suggestion_raw, _re.DOTALL)
        if json_match:
            import json as _json
            parsed = _json.loads(json_match.group())
            suggestions = [str(s).strip() for s in parsed if s][:3]

        # Ensure at least 1 Google Search suggestion is present
        has_google_sug = any("search" in s.lower() or "google" in s.lower() for s in suggestions)
        if not has_google_sug:
            google_q = f"Search Google: {clean_topic}"
            if len(suggestions) >= 3:
                suggestions[2] = google_q
            else:
                suggestions.append(google_q)

        print(f"[Suggestion Engine] Generated {len(suggestions)} suggestions successfully.")
    except Exception as e:
        print(f"[Suggestion Engine] Failed to generate suggestions: {e}")
        clean_topic = _get_clean_topic(query, 45)
        suggestions = [
            f"Can you explain more details about {clean_topic}?",
            f"Search Google: {clean_topic} latest updates",
            f"What are the main advantages and challenges of {clean_topic}?"
        ]

    latency_ms = (time.time() - start_time) * 1000.0

    # 11. Store Dialogue turn to Long-Term Memory (vector index in Qdrant)
    try:
        from services.vector_store.qdrant_service import QdrantService
        from services.embedding_service import EmbeddingService
        import os as _os

        _active_emb = (
            embedding_model
            or _os.getenv("ACTIVE_EMBEDDING_MODEL")
        )

        qdrant_memory = QdrantService(
            collection_name="long_term_memory"
        )

        dialogue_content = (
            f"User: {query}\nAssistant: {response_text}"
        )

        dialogue_emb = EmbeddingService(
            model_name=_active_emb,
            api_key=embedding_api_key,
        ).generate_embedding(dialogue_content)

        from uuid import uuid4
        dialogue_id = str(uuid4())

        qdrant_memory.add_documents(
            ids=[dialogue_id],
            documents=[dialogue_content],
            embeddings=[dialogue_emb],
            metadatas=[{"timestamp": time.time()}]
        )
    except Exception as e:
        print(f"Error saving dialogue exchange to long term memory: {e}")

    # 12. Run RAG Evaluation metrics calculation & SQLite Logging
    c_rel, faith, a_rel = 0.0, 0.0, 0.0
    try:
        eval_context = retrieved_context_str + "\n".join(attachment_parts)
        c_rel, faith, a_rel = await calculate_rag_metrics(
            query=query,
            retrieved_context=eval_context or "",
            response=response_text,
            model_name=data.model,
            is_error=is_technical_error
        )
        memory.add_eval_record(
            query=query,
            context_relevance=c_rel,
            faithfulness=faith,
            answer_relevance=a_rel,
            latency_ms=latency_ms
        )

        # Also persist to PostgreSQL evaluation_results table (visible in PGAdmin)
        try:
            from uuid import uuid4
            from database.session import SessionLocal
            from services.evaluation.evaluation_sql_repository import EvaluationSQLRepository
            from schemas.evaluation.evaluation_result import EvaluationResult

            confidence_score = round((c_rel + faith + a_rel) / 3.0, 3)
            sim_score = 0.0
            if citations:
                scores = [c.get("score") for c in citations if isinstance(c.get("score"), (int, float))]
                if scores:
                    sim_score = round(max(scores), 4)

            eval_result = EvaluationResult(
                evaluation_id=f"eval-{int(time.time() * 1000)}-{uuid4().hex[:8]}",
                review_id=chat_id,
                faithfulness=faith,
                groundedness=c_rel,
                answer_relevance=a_rel,
                answer_correctness=a_rel,
                context_precision=c_rel,
                context_recall=faith,
                citation_accuracy=sim_score,
                hallucination_score=round(1.0 - faith, 3),
                semantic_similarity=sim_score,
                retrieval_score=sim_score,
                overall_score=confidence_score,
                evaluated_by=data.model,
            )

            _eval_db = SessionLocal()
            try:
                EvaluationSQLRepository(_eval_db).create(eval_result)
            finally:
                _eval_db.close()
        except Exception as pg_eval_err:
            print(f"[PG Evaluation Write Error]: {pg_eval_err}")
        eval_step_num = len(pipeline_trace) + 1
        pipeline_trace.append({
            "step": eval_step_num,
            "label": "RAG Evaluation",
            "detail": (
                f"Correctness: {round(a_rel * 100)}% | "
                f"Faithfulness: {round(faith * 100)}% | "
                f"Groundedness: {round(c_rel * 100)}%"
            ),
            "status": "done"
        })
    except Exception as eval_err:
        print(f"[Evaluation Error]: {eval_err}")

    # Compute token cost estimate
    time_taken_s = latency_ms / 1000.0
    model_lower = data.model.lower()
    if "gpt-4o" in model_lower:
        token_cost = "~$0.0025"
    elif "claude" in model_lower:
        token_cost = "~$0.0030"
    elif "gemini" in model_lower:
        token_cost = "~$0.0001"
    elif "groq" in model_lower or "llama-3.3" in model_lower:
        token_cost = "~$0.0005"
    elif "grok" in model_lower:
        token_cost = "~$0.0020"
    else:
        token_cost = "$0.0000 (Local)"

    # Confidence = average of the three metrics
    confidence = round((c_rel + faith + a_rel) / 3.0, 3) if not is_technical_error else 0.0

    metrics_obj = {
        "correctness": round(a_rel * 100),
        "faithfulness": round(faith * 100),
        "groundedness": round(c_rel * 100),
        "confidence": round(confidence * 100),
        "time_taken_s": round(time_taken_s, 2),
        "token_cost": token_cost
    }

    # 13. Save Assistant Message and return
    assistant_msg = memory.add_message(
        conversation_id=chat_id,
        sender="assistant",
        text=response_text,
        citations=citations,
        suggestions=suggestions if suggestions else [],
        metrics=metrics_obj
    )

    # Append live metrics & pipeline trace directly to the response dict (not stored in DB)
    assistant_msg["metrics"] = metrics_obj
    assistant_msg["pipeline_trace"] = pipeline_trace
    assistant_msg["user_message_id"] = user_msg["id"] if user_msg else None

    # 14. Accurately store comprehensive record to Relational DB (chat_history_records)
    try:
        from datetime import datetime, timezone, timedelta
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        timestamp_ist = datetime.now(ist_tz).strftime("%Y-%m-%d %H:%M:%S IST")

        similarity_score = None
        if citations:
            scores = [c.get("score") for c in citations if isinstance(c.get("score"), (int, float))]
            if scores:
                similarity_score = round(max(scores), 4)

        recalled_memory_str = None
        if recalled_memory_str:
            memory_source = "Long-Term Memory"
        elif history and len(history) > 1:
            memory_source = "Short-Term Memory"
        else:
            memory_source = "None"

        files_used_list = []
        chunks_used_list = []
        chunk_meta_list = []
        for c in citations:
            src = c.get("name") or c.get("source")
            if src and src not in files_used_list:
                files_used_list.append(src)
            cid = c.get("id")
            if cid and str(cid) not in chunks_used_list:
                chunks_used_list.append(str(cid))

            meta_parts = []
            idx_val = c.get("chunk_index") or c.get("index")
            if idx_val is not None:
                meta_parts.append(f"Idx:{idx_val}")
            pg = c.get("page") or c.get("page_number")
            if pg is not None:
                meta_parts.append(f"Pg:{pg}")
            txt = c.get("text") or c.get("snippet") or ""
            if txt:
                meta_parts.append(f"Len:{len(txt)}ch")
            tokens = c.get("tokens") or c.get("token_count")
            if tokens:
                meta_parts.append(f"Tok:{tokens}")
            if meta_parts:
                chunk_meta_list.append("; ".join(meta_parts))

        files_used = ", ".join(files_used_list) if files_used_list else None
        chunks_used = ", ".join(chunks_used_list) if chunks_used_list else None
        chunk_metadata = " | ".join(chunk_meta_list) if chunk_meta_list else None

        if urls or url_attached_parts:
            search_source = "Google / Web Search"
        elif should_retrieve and citations:
            search_source = "Vector DB (Local)"
        elif has_attachments:
            search_source = "Direct Attachment"
        else:
            search_source = "LLM Direct Knowledge"

        rec_id = f"rec-{int(time.time() * 1000)}-{uuid4().hex[:6]}"
        memory.add_history_record(
            record_id=rec_id,
            timestamp_ist=timestamp_ist,
            user_prompt=query,
            retrieved_response=response_text,
            response_metrics=metrics_obj,
            timetaken_s=round(time_taken_s, 2),
            similarity_score=similarity_score,
            llm_model=data.model,
            memory_source=memory_source,
            files_used=files_used,
            chunks_used=chunks_used,
            chunk_metadata=chunk_metadata,
            search_source=search_source
        )
    except Exception as log_err:
        print(f"[History Record Logging Error]: {log_err}")

    # 15. Automatically capture user interaction to Dataset Collection (data/query_dataset/*.json)
    try:
        from services.dataset_service import DatasetService
        retrieved_chunk_text = [c.get("snippet") or c.get("text") for c in citations if (c.get("snippet") or c.get("text"))]

        dataset_record = DatasetService.save_interaction(
            query=query,
            conversation_id=chat_id,
            llm_response=response_text,
            retrieved_chunk_ids=chunks_used_list if 'chunks_used_list' in locals() else [],
            retrieved_chunk_text=retrieved_chunk_text,
            source_documents=files_used_list if 'files_used_list' in locals() else [],
            retrieval_score=similarity_score if 'similarity_score' in locals() else None,
            feedback="unrated",
            metadata={
                "model": data.model,
                "metrics": metrics_obj
            }
        )
        assistant_msg["interaction_id"] = dataset_record["interaction_id"]
    except Exception as ds_err:
        print(f"[Dataset Logging Error]: {ds_err}")

    return assistant_msg



# Additional Router for History & CSV Analytics Endpoints
from fastapi import APIRouter
from fastapi.responses import Response

history_router = APIRouter(prefix="/history", tags=["History & Analytics"])

@history_router.get("")
async def get_chat_history_records(memory = Depends(get_memory)):
    """Retrieve full relational chat history analytics records."""
    return memory.get_history_records(limit=500)

@history_router.delete("")
async def clear_all_history_records(memory = Depends(get_memory)):
    """Clear all chat history records."""
    memory.clear_all_history_records()
    return {"message": "All history records cleared successfully"}

@history_router.delete("/{record_id}")
async def delete_single_history_record(record_id: str, memory = Depends(get_memory)):
    """Delete a single history record by ID."""
    success = memory.delete_history_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="History record not found")
    return {"message": f"History record {record_id} deleted successfully"}

@history_router.get("/csv")
async def download_chat_history_csv(memory = Depends(get_memory)):
    """Generate and return CSV file download of all history records."""
    import csv
    import io

    records = memory.get_history_records(limit=1000)
    output = io.StringIO()
    writer = csv.writer(output)

    # Required CSV Column Headers in Order
    writer.writerow([
        "Unique ID",
        "Timestamp (IST)",
        "User Prompt",
        "Retrieved Response",
        "Response Metrics",
        "Time Taken (s)",
        "Similarity Score",
        "LLM Model Used",
        "Memory Source",
        "File(s) Used",
        "Chunk(s) Used",
        "Chunk Metadata",
        "Search Source"
    ])

    for r in records:
        m = r.get("response_metrics") or {}
        metrics_str = f"Correctness: {m.get('correctness', 0)}%, Faithfulness: {m.get('faithfulness', 0)}%, Groundedness: {m.get('groundedness', 0)}%, Confidence: {m.get('confidence', 0)}%"
        writer.writerow([
            r.get("id") or "NULL",
            r.get("timestamp_ist") or "NULL",
            r.get("user_prompt") or "NULL",
            r.get("retrieved_response") or "NULL",
            metrics_str,
            r.get("timetaken_s") if r.get("timetaken_s") is not None else "NULL",
            r.get("similarity_score") if r.get("similarity_score") is not None else "NULL",
            r.get("llm_model") or "NULL",
            r.get("memory_source") or "NULL",
            r.get("files_used") or "NULL",
            r.get("chunks_used") or "NULL",
            r.get("chunk_metadata") or "NULL",
            r.get("search_source") or "NULL"
        ])

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=chat_history_analytics.csv"
        }
    )
