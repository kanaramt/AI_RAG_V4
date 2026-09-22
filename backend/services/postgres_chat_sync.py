from sqlalchemy.orm import Session

from backend.database.session import SessionLocal
from backend.database.models.conversation_model import ConversationModel
from backend.database.models.message_model import MessageModel
from backend.database.models.chat_history_record_model import ChatHistoryRecordModel


class PostgresChatSync:

    @staticmethod
    def save_conversation(
        conversation_id: str,
        title: str,
        model: str,
    ):
        db: Session = SessionLocal()

        try:
            existing = (
                db.query(ConversationModel)
                .filter(
                    ConversationModel.conversation_id == conversation_id
                )
                .first()
            )

            if existing:
                return

            db.add(
                ConversationModel(
                    conversation_id=conversation_id,
                    title=title,
                    model=model,
                )
            )

            db.commit()

        finally:
            db.close()

    @staticmethod
    def save_message(
        message_id: str,
        conversation_id: str,
        sender: str,
        text: str,
        attachments=None,
        citations=None,
    ):
        db: Session = SessionLocal()

        try:
            existing = (
                db.query(MessageModel)
                .filter(
                    MessageModel.message_id == message_id
                )
                .first()
            )

            if existing:
                return

            db.add(
                MessageModel(
                    message_id=message_id,
                    conversation_id=conversation_id,
                    sender=sender,
                    text=text,
                    attachments=attachments,
                    citations=citations,
                )
            )

            db.commit()

        finally:
            db.close()

    @staticmethod
    def save_history_record(
        record_id: str,
        conversation_id: str,
        timestamp_ist,
        user_prompt: str,
        retrieved_response: str,
        response_metrics: dict,
        similarity_score: float,
        llm_model: str,
        memory_source: str,
        files_used,
        chunks_used,
        chunk_metadata,
        search_source: str,
    ):
        db: Session = SessionLocal()

        try:
            print("POSTGRES HISTORY SYNC CALLED")
            existing = (
                db.query(ChatHistoryRecordModel)
                .filter(
                    ChatHistoryRecordModel.record_id == record_id
                )
                .first()
            )

            if existing:
                return

            metrics = response_metrics or {}

            db.add(
                ChatHistoryRecordModel(
                    record_id=record_id,
                    conversation_id=conversation_id,
                    timestamp_ist=timestamp_ist,
                    user_prompt=user_prompt,
                    retrieved_response=retrieved_response,
                    correctness_score=float(metrics.get("correctness", 0)),
                    faithfulness_score=float(metrics.get("faithfulness", 0)),
                    groundedness_score=float(metrics.get("groundedness", 0)),
                    confidence_score=float(metrics.get("confidence", 0)),
                    time_taken_seconds=float(metrics.get("time_taken_s", 0)),
                    similarity_score=similarity_score or 0,
                    llm_model=llm_model,
                    memory_source=memory_source,
                    files_used=files_used,
                    chunks_used=chunks_used,
                    chunk_metadata=chunk_metadata,
                    search_source=search_source,
                )
            )

            db.commit()

        except Exception as e:
            print(f"[POSTGRES HISTORY ERROR] {e}")
            db.rollback()

        finally:
            db.close()