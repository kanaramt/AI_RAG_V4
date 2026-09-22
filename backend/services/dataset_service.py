import os
import json
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional

DATASET_DIR = os.path.join(os.getcwd(), "data", "query_dataset")
os.makedirs(DATASET_DIR, exist_ok=True)

class DatasetService:
    """
    Manages capturing, querying, and exporting user interaction logs for RAG fine-tuning & evaluation.
    """

    @staticmethod
    def save_interaction(
        query: str,
        conversation_id: str,
        llm_response: str,
        retrieved_chunk_ids: Optional[List[str]] = None,
        retrieved_chunk_text: Optional[List[str]] = None,
        source_documents: Optional[List[str]] = None,
        retrieval_score: Optional[float] = None,
        feedback: str = "unrated",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Saves a single user interaction to data/query_dataset/<interaction_id>.json
        """
        now = datetime.now()
        timestamp_iso = now.isoformat()
        # Use a stable, unique interaction_id that matches the filename exactly.
        # Format: interaction_<epoch_ms>_<chat_id_short> for easy human readability & lookup.
        epoch_ms = int(now.timestamp() * 1000)
        conv_short = (conversation_id or "unknown")[:12]
        interaction_id = f"interaction_{epoch_ms}_{conv_short}"
        
        record = {
            "interaction_id": interaction_id,
            "query": query,
            "timestamp": timestamp_iso,
            "conversation_id": conversation_id,
            "retrieved_chunk_ids": retrieved_chunk_ids or [],
            "retrieved_chunk_text": retrieved_chunk_text or [],
            "source_documents": source_documents or [],
            "llm_response": llm_response,
            "retrieval_score": round(retrieval_score, 4) if retrieval_score is not None else None,
            "feedback": feedback,
            "metadata": metadata or {}
        }

        # Filename == interaction_id + .json so update_feedback can reliably locate it.
        filename = f"{interaction_id}.json"
        filepath = os.path.join(DATASET_DIR, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False)
            print(f"[Dataset] Saved RAG Dataset Interaction: {filename}")
        except Exception as e:
            print(f"[Dataset Warning] Failed to save dataset record: {e}")

        return record

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Returns dataset metrics: Total Queries, Positive Count, Negative Count, Size in Bytes & Formatted.
        """
        files = glob.glob(os.path.join(DATASET_DIR, "*.json"))
        total_queries = len(files)
        positive_count = 0
        negative_count = 0
        total_size_bytes = 0

        for filepath in files:
            try:
                size = os.path.getsize(filepath)
                total_size_bytes += size

                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    fb = data.get("feedback", "").lower()
                    if fb == "positive":
                        positive_count += 1
                    elif fb == "negative":
                        negative_count += 1
            except Exception as e:
                print(f"Error reading dataset file {filepath}: {e}")

        # Format human-readable size
        def format_size(bytes_val: int) -> str:
            if bytes_val == 0:
                return "0 Bytes"
            units = ["Bytes", "KB", "MB", "GB"]
            i = 0
            while bytes_val >= 1024 and i < len(units) - 1:
                bytes_val /= 1024.0
                i += 1
            return f"{bytes_val:.2f} {units[i]}"

        return {
            "total_queries": total_queries,
            "positive_feedback_count": positive_count,
            "negative_feedback_count": negative_count,
            "dataset_size_bytes": total_size_bytes,
            "dataset_size_formatted": format_size(total_size_bytes)
        }

    @staticmethod
    def get_queries(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        feedback_type: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves interaction records matching filter parameters.
        """
        files = glob.glob(os.path.join(DATASET_DIR, "*.json"))
        records = []

        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    record = json.load(f)

                # Date filtering (ISO format or YYYY-MM-DD)
                ts = record.get("timestamp", "")
                if start_date and ts < start_date:
                    continue
                if end_date and ts > (end_date + "T23:59:59"):
                    continue

                # Feedback filtering
                fb = record.get("feedback", "unrated").lower()
                if feedback_type and feedback_type != "all":
                    if feedback_type == "positive" and fb != "positive":
                        continue
                    if feedback_type == "negative" and fb != "negative":
                        continue
                    if feedback_type == "unrated" and fb != "unrated":
                        continue

                # Conversation ID filtering
                cid = record.get("conversation_id", "")
                if conversation_id and conversation_id.strip():
                    if conversation_id.strip().lower() not in cid.lower():
                        continue

                records.append(record)
            except Exception as e:
                print(f"Error parsing record {filepath}: {e}")

        # Sort descending by timestamp
        records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        return records

    @staticmethod
    def update_feedback(interaction_id: str, feedback: str) -> bool:
        """
        Updates user feedback for a given interaction record.
        First tries direct filename match (interaction_id.json), then falls back
        to scanning all JSON files for matching interaction_id field.
        """
        # Fast path: filename == interaction_id + .json (new consistent format)
        direct_path = os.path.join(DATASET_DIR, f"{interaction_id}.json")
        if os.path.exists(direct_path):
            try:
                with open(direct_path, "r", encoding="utf-8") as f:
                    record = json.load(f)
                record["feedback"] = feedback
                with open(direct_path, "w", encoding="utf-8") as f:
                    json.dump(record, f, indent=2, ensure_ascii=False)
                print(f"[Dataset] Updated feedback to '{feedback}' for {interaction_id}")
                return True
            except Exception as e:
                print(f"Error updating feedback (direct path) for {interaction_id}: {e}")

        # Fallback: scan all JSON files for matching interaction_id field (supports legacy files)
        files = glob.glob(os.path.join(DATASET_DIR, "*.json"))
        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    record = json.load(f)
                # Match on interaction_id field OR if the id appears anywhere in filepath
                if record.get("interaction_id") == interaction_id or interaction_id in os.path.basename(filepath):
                    record["feedback"] = feedback
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(record, f, indent=2, ensure_ascii=False)
                    print(f"[Dataset] Updated feedback to '{feedback}' for {interaction_id} (legacy scan)")
                    return True
            except Exception as e:
                print(f"Error updating feedback for {interaction_id}: {e}")
        return False

