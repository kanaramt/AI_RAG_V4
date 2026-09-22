from fastapi import APIRouter
from sqlalchemy import text

from database import get_db

router = APIRouter(
    prefix="/database",
    tags=["Database"],
)


@router.get("/health")
async def database_health():

    db = next(get_db())

    try:

        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as ex:

        return {
            "status": "failed",
            "error": str(ex),
        }

    finally:

        db.close()


@router.post("/query")
async def execute_sql_query(payload: dict):
    sql = (payload.get("sql") or "").strip()
    if not sql:
        return {"error": "SQL query string is required", "columns": [], "rows": []}
    
    db = next(get_db())
    try:
        res = db.execute(text(sql))
        if res.returns_rows:
            columns = list(res.keys())
            rows = [dict(row._mapping) for row in res.fetchall()]
            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "count": len(rows)
            }
        else:
            db.commit()
            return {
                "success": True,
                "message": "Query executed successfully",
                "columns": ["Result"],
                "rows": [{"Result": "Query executed successfully"}],
                "count": 1
            }
    except Exception as ex:
        return {
            "success": False,
            "error": str(ex),
            "columns": [],
            "rows": []
        }
    finally:
        db.close()
