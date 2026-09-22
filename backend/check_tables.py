from sqlalchemy import text

from database.database import engine

with engine.connect() as conn:
    rows = conn.execute(
        text(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname='public'
            ORDER BY tablename
            """
        )
    )

    print("\nPOSTGRES TABLES\n")

    for row in rows:
        print(row[0])
