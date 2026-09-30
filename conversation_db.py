from sqlalchemy import text
from database import SessionLocal


def save_summary(user_id, session_id, summary):
    db = SessionLocal()
    try:
        query = text("""
            INSERT INTO conversation_summaries (user_id, session_id, summary)
            VALUES (:user_id, :session_id, :summary)
            ON CONFLICT (user_id, session_id)
            DO UPDATE SET
                summary = EXCLUDED.summary,
                updated_at = CURRENT_TIMESTAMP
        """)
        db.execute(query, {
            "user_id": user_id,
            "session_id": session_id,
            "summary": summary
        })
        db.commit()
    finally:
        db.close()
def get_summary(user_id, session_id):
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                SELECT summary FROM conversation_summaries
                WHERE user_id = :user_id AND session_id = :session_id
            """),
            {"user_id": user_id, "session_id": session_id}
        ).fetchone()
        return row[0] if row else None
    finally:
        db.close()