import os
import sqlite3
import json
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Any
from services.postgres_chat_sync import PostgresChatSync
from settings import settings

class MemoryService:
    """
    Enterprise Chat Memory and Registry Manager using SQLite.
    
    Stores:
    - Conversations (Sessions)
    - Messages (History)
    - Documents (Metadata Registry)
    - RAG Metrics Evaluations (Performance tracking)
    """

    def __init__(self):
        db_dir = settings.BACKEND_DIR / "data" / "database_files"
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = str(db_dir / "chat_history.db")
        
        # Automatically organize & migrate legacy .db files into backend/data/database_files
        legacy_dirs = [
            settings.BACKEND_DIR / "data",
            settings.BACKEND_DIR / "data" / "database",
            settings.BACKEND_DIR / "data" / "database .db files"
        ]
        for legacy_data_dir in legacy_dirs:
            if legacy_data_dir.exists() and legacy_data_dir != db_dir:
                for db_file in ["chat_history.db", "chat_history.db-shm", "chat_history.db-wal"]:
                    legacy_file = legacy_data_dir / db_file
                    target_file = db_dir / db_file
                    if legacy_file.exists() and not target_file.exists():
                        try:
                            import shutil
                            shutil.move(str(legacy_file), str(target_file))
                            print(f"[MemoryService] Organized & moved legacy DB file '{db_file}' to backend/data/database_files/")
                        except Exception as e:
                            print(f"[MemoryService] Warning moving legacy DB file: {e}")
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        try:
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA synchronous=NORMAL;")
        except Exception as e:
            print(f"Warning: could not set WAL mode on SQLite: {e}")
        self.create_tables()


    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Conversations Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Messages Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                attachments TEXT, -- JSON array of staged files
                citations TEXT,   -- JSON array of retrieved sources
                suggestions TEXT, -- JSON array of suggestion strings
                metrics TEXT,     -- JSON metrics string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')
        # Backward compat: add suggestions column if not exists (for existing DBs)
        try:
            cursor.execute('ALTER TABLE messages ADD COLUMN suggestions TEXT')
        except Exception:
            pass  # Column already exists

        # Backward compat: add metrics column if not exists
        try:
            cursor.execute('ALTER TABLE messages ADD COLUMN metrics TEXT')
        except Exception:
            pass  # Column already exists

        # Evaluation parameters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rag_evaluation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                query TEXT,
                context_relevance REAL,
                faithfulness REAL,
                answer_relevance REAL,
                latency_ms REAL
            )
        ''')

        # Ingested Documents Registry Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                size TEXT NOT NULL,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Full Detailed Chat History & Analytics Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history_records (
                id TEXT PRIMARY KEY,
                timestamp_ist TEXT NOT NULL,
                user_prompt TEXT NOT NULL,
                retrieved_response TEXT NOT NULL,
                response_metrics TEXT,
                timetaken_s REAL,
                similarity_score REAL,
                llm_model TEXT NOT NULL,
                memory_source TEXT,
                files_used TEXT,
                chunks_used TEXT,
                chunk_metadata TEXT,
                search_source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        try:
            cursor.execute('ALTER TABLE chat_history_records ADD COLUMN chunk_metadata TEXT')
        except Exception:
            pass  # Column already exists
        
        self.conn.commit()

    # --- Conversations CRUD ---
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title, model, created_at FROM conversations ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def create_conversation(self, chat_id: str, title: str, model: str) -> Dict[str, Any]:
        cursor = self.conn.cursor()

        cursor.execute(
            'INSERT INTO conversations (id, title, model) VALUES (?, ?, ?)',
            (chat_id, title, model)
        )

        self.conn.commit()

        PostgresChatSync.save_conversation(
            conversation_id=chat_id,
            title=title,
            model=model,
        )

        return {
            'id': chat_id,
            'title': title,
            'model': model,
        }

    def get_conversation(self, chat_id: str) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title, model FROM conversations WHERE id = ?', (chat_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def rename_conversation(self, chat_id: str, new_title: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('UPDATE conversations SET title = ? WHERE id = ?', (new_title, chat_id))
        self.conn.commit()
        return cursor.rowcount > 0


    def delete_conversation(self, chat_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute('DELETE FROM conversations WHERE id = ?', (chat_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # --- Messages CRUD ---

    def add_message(self, conversation_id: str, sender: str, text: str, attachments: List[Dict] = None, citations: List[Dict] = None, suggestions: List[str] = None, metrics: Dict = None) -> Dict[str, Any]:
        msg_id = f"msg-{int(datetime.now().timestamp() * 1000)}-{uuid4().hex[:8]}"
        attachments_json = json.dumps(attachments) if attachments else None
        citations_json = json.dumps(citations) if citations else None
        suggestions_json = json.dumps(suggestions) if suggestions else None
        metrics_json = json.dumps(metrics) if metrics else None
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO messages (id, conversation_id, sender, text, attachments, citations, suggestions, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (msg_id, conversation_id, sender, text, attachments_json, citations_json, suggestions_json, metrics_json))
        self.conn.commit()

        PostgresChatSync.save_message(
            message_id=msg_id,
            conversation_id=conversation_id,
            sender=sender,
            text=text,
            attachments=attachments,
            citations=citations,
        )
        
        return {
            'id': msg_id,
            'conversation_id': conversation_id,
            'sender': sender,
            'text': text,
            'attachments': attachments or [],
            'citations': citations or [],
            'suggestions': suggestions or [],
            'metrics': metrics
        }

    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, sender, text, attachments, citations, suggestions, metrics, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC', (conversation_id,))
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            msg = dict(row)
            msg['attachments'] = json.loads(msg['attachments']) if msg['attachments'] else []
            msg['citations'] = json.loads(msg['citations']) if msg['citations'] else []
            msg['suggestions'] = json.loads(msg['suggestions']) if msg.get('suggestions') else []
            msg['metrics'] = json.loads(msg['metrics']) if msg.get('metrics') else None
            messages.append(msg)
            
        return messages

    def truncate_messages(self, conversation_id: str, before_message_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT created_at FROM messages WHERE id = ?', (before_message_id,))
        row = cursor.fetchone()
        if row:
            created_at = row['created_at']
            cursor.execute('DELETE FROM messages WHERE conversation_id = ? AND created_at >= ?', (conversation_id, created_at))
            self.conn.commit()
            return True
        return False

    # --- RAG Evaluation metrics ---

    def add_eval_record(self, query: str, context_relevance: float, faithfulness: float, answer_relevance: float, latency_ms: float):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO rag_evaluation (query, context_relevance, faithfulness, answer_relevance, latency_ms)
            VALUES (?, ?, ?, ?, ?)
        ''', (query, context_relevance, faithfulness, answer_relevance, latency_ms))
        self.conn.commit()

    def get_eval_stats(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                AVG(context_relevance) as avg_c,
                AVG(faithfulness) as avg_f,
                AVG(answer_relevance) as avg_a,
                AVG(latency_ms) as avg_l,
                COUNT(*) as total_evals
            FROM rag_evaluation
        ''')
        hist_row = cursor.fetchone()
        
        cursor.execute('''
            SELECT context_relevance, faithfulness, answer_relevance, latency_ms, query
            FROM rag_evaluation
            ORDER BY timestamp DESC LIMIT 1
        ''')
        latest_row = cursor.fetchone()
        
        hist = dict(hist_row) if hist_row else {}
        latest = dict(latest_row) if latest_row else {}
        
        def _val(d: dict, key: str, default: float = 0.0) -> float:
            v = d.get(key)
            return float(v) if v is not None else default

        return {
            "historical": {
                "context_relevance": round(_val(hist, 'avg_c', 0.0), 3),
                "faithfulness": round(_val(hist, 'avg_f', 0.0), 3),
                "answer_relevance": round(_val(hist, 'avg_a', 0.0), 3),
                "latency_ms": round(_val(hist, 'avg_l', 0.0), 1),
                "total_queries": hist.get('total_evals') or 0
            },
            "current": {
                "context_relevance": round(_val(latest, 'context_relevance', 0.0), 3),
                "faithfulness": round(_val(latest, 'faithfulness', 0.0), 3),
                "answer_relevance": round(_val(latest, 'answer_relevance', 0.0), 3),
                "latency_ms": round(_val(latest, 'latency_ms', 0.0), 1),
                "query": latest.get('query') or "No queries analyzed yet"
            }
        }

    # --- Document Registry CRUD ---

    def add_document(self, doc_id: str, name: str, size: str, doc_type: str, path: str) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO documents (id, name, size, type, path)
            VALUES (?, ?, ?, ?, ?)
        ''', (doc_id, name, size, doc_type, path))
        self.conn.commit()
        return {'id': doc_id, 'name': name, 'size': size, 'type': doc_type, 'path': path}

    def list_documents(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, size, type, path, created_at FROM documents ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, size, type, path FROM documents WHERE id = ?', (doc_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def delete_document(self, doc_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def clear_all_documents(self) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM documents')
        self.conn.commit()
        return True

    # --- Chat History & Analytics Records CRUD ---

    def add_history_record(
        self,
        record_id: str,
        timestamp_ist: str,
        user_prompt: str,
        retrieved_response: str,
        response_metrics: dict,
        timetaken_s: float,
        similarity_score: float = None,
        llm_model: str = "llama3:8b",
        memory_source: str = "None",
        files_used: str = None,
        chunks_used: str = None,
        chunk_metadata: str = None,
        search_source: str = "LLM Direct Knowledge"
    ) -> Dict[str, Any]:
        metrics_json = json.dumps(response_metrics) if response_metrics else None
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO chat_history_records (
                id, timestamp_ist, user_prompt, retrieved_response, response_metrics,
                timetaken_s, similarity_score, llm_model, memory_source,
                files_used, chunks_used, chunk_metadata, search_source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record_id, timestamp_ist, user_prompt, retrieved_response, metrics_json,
            timetaken_s, similarity_score, llm_model, memory_source,
            files_used, chunks_used, chunk_metadata, search_source
        ))

        print("SQLITE HISTORY SAVED", record_id)
        self.conn.commit()

        PostgresChatSync.save_history_record(
            record_id=record_id,
            conversation_id="legacy",
            timestamp_ist=timestamp_ist,
            user_prompt=user_prompt,
            retrieved_response=retrieved_response,
            response_metrics=response_metrics,
            similarity_score=similarity_score,
            llm_model=llm_model,
            memory_source=memory_source,
            files_used=files_used,
            chunks_used=chunks_used,
            chunk_metadata=chunk_metadata,
            search_source=search_source,
        )


        return {
            "id": record_id,
            "timestamp_ist": timestamp_ist,
            "user_prompt": user_prompt,
            "retrieved_response": retrieved_response,
            "response_metrics": response_metrics,
            "timetaken_s": timetaken_s,
            "similarity_score": similarity_score,
            "llm_model": llm_model,
            "memory_source": memory_source,
            "files_used": files_used,
            "chunks_used": chunks_used,
            "chunk_metadata": chunk_metadata,
            "search_source": search_source
        }

    def get_history_records(self, limit: int = 500) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, timestamp_ist, user_prompt, retrieved_response, response_metrics,
                   timetaken_s, similarity_score, llm_model, memory_source,
                   files_used, chunks_used, chunk_metadata, search_source, created_at
            FROM chat_history_records
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        records = []
        for r in rows:
            d = dict(r)
            d['response_metrics'] = json.loads(d['response_metrics']) if d['response_metrics'] else {}
            records.append(d)
        return records

    def delete_history_record(self, record_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM chat_history_records WHERE id = ?', (record_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def clear_all_history_records(self) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM chat_history_records')
        self.conn.commit()
        return True

    def close(self):
        self.conn.close()

