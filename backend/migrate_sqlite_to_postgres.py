import sqlite3
import json
from datetime import datetime
from database.session import SessionLocal
from database.models.conversation_model import ConversationModel
from database.models.message_model import MessageModel
from database.models.chat_history_record_model import ChatHistoryRecordModel


SQLITE_DB = r"backend\data\database_files\chat_history.db"


def migrate_conversations():
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM conversations
        """
    ).fetchall()

    db = SessionLocal()

    try:
        for row in rows:

            exists = (
                db.query(ConversationModel)
                .filter(
                    ConversationModel.conversation_id == row["id"]
                )
                .first()
            )

            if exists:
                continue

            db.add(
                ConversationModel(
                    conversation_id=row["id"],
                    title=row["title"],
                    model=row["model"],
                )
            )

        db.commit()

    finally:
        db.close()

    print(f"Conversations migrated: {len(rows)}")


def migrate_messages():
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM messages
        """
    ).fetchall()

    db = SessionLocal()

    try:
        for row in rows:

            exists = (
                db.query(MessageModel)
                .filter(
                    MessageModel.message_id == row["id"]
                )
                .first()
            )

            if exists:
                continue

            attachments = None
            citations = None

            try:
                if row["attachments"]:
                    attachments = json.loads(row["attachments"])
            except Exception:
                pass

            try:
                if row["citations"]:
                    citations = json.loads(row["citations"])
            except Exception:
                pass

            db.add(
                MessageModel(
                    message_id=row["id"],
                    conversation_id=row["conversation_id"],
                    sender=row["sender"],
                    text=row["text"],
                    attachments=attachments,
                    citations=citations,
                )
            )

        db.commit()

    finally:
        db.close()

    print(f"Messages migrated: {len(rows)}")

def migrate_chat_history_records():
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM chat_history_records
        """
    ).fetchall()

    db = SessionLocal()

    try:
        for row in rows:

            exists = (
                db.query(ChatHistoryRecordModel)
                .filter(
                    ChatHistoryRecordModel.record_id == row["id"]
                )
                .first()
            )

            if exists:
                continue

            metrics = {}

            try:
                if row["response_metrics"]:
                    metrics = json.loads(row["response_metrics"])
            except Exception:
                pass

            db.add(
                ChatHistoryRecordModel(
                    record_id=row["id"],
                    conversation_id="migration",
                    user_prompt=row["user_prompt"],
                    retrieved_response=row["retrieved_response"],
                    correctness_score=float(metrics.get("correctness", 0)),
                    faithfulness_score=float(metrics.get("faithfulness", 0)),
                    groundedness_score=float(metrics.get("groundedness", 0)),
                    confidence_score=float(metrics.get("confidence", 0)),
                    time_taken_seconds=float(row["timetaken_s"] or 0),
                    similarity_score=float(row["similarity_score"] or 0),
                    llm_model=row["llm_model"],
                    memory_source=row["memory_source"],
                    search_source=row["search_source"],
                )
            )

        db.commit()

    finally:
        db.close()

    print(f"History records migrated: {len(rows)}")

if __name__ == "__main__":
    migrate_conversations()
    migrate_messages()
    migrate_chat_history_records()
