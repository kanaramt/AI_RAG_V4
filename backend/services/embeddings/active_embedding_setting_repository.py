from database.session import SessionLocal
from database.models.active_embedding_setting import ActiveEmbeddingSettingModel


class ActiveEmbeddingSettingRepository:
    SETTING_KEY = "default"

    @classmethod
    def get_active_model(cls) -> str | None:
        db = SessionLocal()
        try:
            row = (
                db.query(ActiveEmbeddingSettingModel)
                .filter(
                    ActiveEmbeddingSettingModel.setting_key == cls.SETTING_KEY
                )
                .first()
            )
            return row.model_id if row else None
        finally:
            db.close()

    @classmethod
    def save_active_model(cls, model_id: str) -> None:
        db = SessionLocal()
        try:
            row = (
                db.query(ActiveEmbeddingSettingModel)
                .filter(
                    ActiveEmbeddingSettingModel.setting_key == cls.SETTING_KEY
                )
                .first()
            )

            if row:
                row.model_id = model_id
            else:
                db.add(
                    ActiveEmbeddingSettingModel(
                        setting_key=cls.SETTING_KEY,
                        model_id=model_id,
                    )
                )

            db.commit()
        finally:
            db.close()
