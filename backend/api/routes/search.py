"""
Web Search Route — DuckDuckGo-based web search with LLM synthesis.
No API key required. Uses DuckDuckGo HTML endpoint for free, fast web search.
"""
import re
import urllib.request
import urllib.parse
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

router = APIRouter()

class SearchRequest(BaseModel):
    query: str | None = None
    q: str | None = None
    text: str | None = None
    model: str | None = "llama3"
    chat_id: str | None = None

def fetch_ddg_results(search_query: str, max_results: int = 6) -> list[dict]:
    search_query = (search_query or "").strip()
    if not search_query:
        return []
    
    data = urllib.parse.urlencode({'q': search_query}).encode('utf-8')
    req = urllib.request.Request(
        'https://html.duckduckgo.com/html/',
        data=data,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[Web Search] DDG fetch failed: {e}")
        return []
    
    def strip_tags(t: str) -> str:
        t = re.sub(r'<[^>]+>', '', t)
        t = t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ').replace('&#x27;', "'")
        return t.strip()

    results = []
    blocks = re.split(r'class="[^"]*result__body[^"]*"', html)
    for block in blocks[1:]:
        title_match = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
        url_match = re.search(r'href="([^"]+)"', block)
        snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL)
        if not snippet_match:
            snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</span>', block, re.DOTALL)
        
        title = strip_tags(title_match.group(1)) if title_match else ""
        snippet = strip_tags(snippet_match.group(1)) if snippet_match else ""
        raw_url = url_match.group(1) if url_match else ""
        
        clean_url = raw_url
        if "uddg=" in raw_url:
            match_u = re.search(r'uddg=([^&]+)', raw_url)
            if match_u:
                clean_url = urllib.parse.unquote(match_u.group(1))
                
        if title or snippet:
            results.append({
                "title": title,
                "snippet": snippet,
                "url": clean_url
            })
            
        if len(results) >= max_results:
            break
            
    return results

async def _process_web_search(search_query: str, model_name: str = "llama3", chat_id: str | None = None):
    search_query = (search_query or "").strip()
    if not search_query:
        raise HTTPException(status_code=400, detail="Search query is required.")

    # 1. Fetch web search results from DDG
    web_results = fetch_ddg_results(search_query, max_results=6)
    
    # Build instant AI Overview text summary from live web results as guaranteed fallback
    web_markdown_summary = ""
    if web_results:
        summary_lines = [f"### 🌐 AI Overview for *\"{search_query}\"*\n"]
        for idx, r in enumerate(web_results):
            snippet = r.get("snippet", "").strip()
            if snippet:
                summary_lines.append(f"• {snippet}")
        web_markdown_summary = "\n\n".join(summary_lines)
    else:
        web_markdown_summary = f"No live web search details found for *\"{search_query}\"*. Please try rephrasing your search."

    context_text = "\n\n".join(
        f"[{idx+1}] Source: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
        for idx, r in enumerate(web_results)
    ) if web_results else "No direct web search snippets retrieved."

    # 2. Fast LLM Synthesis in Google AI Overview style (No raw URLs in text body)
    synthesis = web_markdown_summary
    try:
        from llm.factory import LLMFactory
        llm = LLMFactory.get_llm_by_model(model_name, temperature=0.3)
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI Search Assistant providing a Google AI Overview style response. "
                    "Synthesize a comprehensive, well-structured, clear explanation of the user's prompt using the provided search context. "
                    "CRITICAL REQUIREMENT: Do NOT include raw URLs, markdown link syntax like [title](url), or lists of links in your response body. "
                    "Provide a clean, informative answer with subheadings, bullet points, key takeaways, and clear explanations. "
                    "All source link citations will be displayed in the dedicated RAG Sources section."
                )
            },
            {
                "role": "user",
                "content": (
                    f"User Prompt: {search_query}\n\n"
                    f"Web Search Information:\n{context_text}\n\n"
                    "Provide a detailed, clean AI Overview explanation without inline URLs."
                )
            }
        ]
        
        import asyncio
        llm_task = asyncio.create_task(llm.chat(prompt_messages))
        synthesis_result = await asyncio.wait_for(llm_task, timeout=5.5)
        if synthesis_result and len(synthesis_result.strip()) > 30:
            synthesis = synthesis_result
    except Exception as err:
        print(f"[Web Search Fast Fallback]: Using live web markdown summary ({err})")

    # Clean up any stray markdown links or raw URLs from response text
    synthesis = re.sub(r'\[([^\]]+)\]\(https?://[^\)]+\)', r'\1', synthesis)
    synthesis = re.sub(r'https?://[^\s\)]+', '', synthesis)

    # 3. Save user query and assistant response to chat memory safely
    assistant_msg = None
    if chat_id:
        try:
            from dependencies import get_memory
            memory = get_memory()
            
            # Ensure conversation exists in memory before adding messages
            if not memory.get_conversation(chat_id):
                memory.create_conversation(title=f"Web Search: {search_query[:20]}", model=model_name, chat_id=chat_id)

            # Save user prompt message to conversation memory
            user_msg = None
            try:
                user_msg = memory.add_message(
                    conversation_id=chat_id,
                    sender="user",
                    text=search_query
                )
            except Exception as u_err:
                print(f"[Web Search User Msg Save Error]: {u_err}")

            citations = [
                {
                    "name": r["title"],
                    "source": r["url"],
                    "snippet": r["snippet"],
                    "score": 1.0
                }
                for r in web_results
            ]
            assistant_msg = memory.add_message(
                conversation_id=chat_id,
                sender="assistant",
                text=synthesis,
                citations=citations,
                suggestions=[
                    f"🌐 Search Google: {search_query} latest updates",
                    f"Explain more about {search_query[:30]}",
                    f"Summarize key facts of {search_query[:30]}"
                ]
            )
        except Exception as mem_err:
            print(f"[Web Search Memory Error]: {mem_err}")

    return JSONResponse(content={
        "query": search_query,
        "synthesis": synthesis,
        "results": web_results,
        "message": assistant_msg,
        "user_message_id": user_msg["id"] if user_msg else None
    })

@router.post("/search")
async def execute_web_search_post(req: SearchRequest):
    search_query = req.query or req.q or req.text or ""
    model_name = req.model or "llama3"
    return await _process_web_search(search_query=search_query, model_name=model_name, chat_id=req.chat_id)

@router.get("/search")
async def execute_web_search_get(
    query: str = Query(...),
    model: str = Query("llama3"),
    chat_id: str | None = Query(None)
):
    return await _process_web_search(search_query=query, model_name=model, chat_id=chat_id)

