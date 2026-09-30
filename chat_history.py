from sqlalchemy import text
from database import SessionLocal


def save_message(user_id, session_id, role, message):

    db = SessionLocal()

    try:
        db.execute(
            text("""
                INSERT INTO chat_messages
                (user_id, session_id, role, message)
                VALUES
                (:user_id, :session_id, :role, :message)
            """),
            {
                "user_id": user_id,
                "session_id": session_id,
                "role": role,
                "message": message,
            }
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_history(user_id, session_id, limit=10):
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT role, message, created_at
                FROM chat_messages
                WHERE user_id = :user_id
                  AND session_id = :session_id
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {
                "user_id": user_id,
                "session_id": session_id,
                "limit": limit
            }
        )
        rows = result.fetchall()
        return list(reversed(rows))
    finally:
        db.close()
def get_message_count(user_id, session_id):
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT COUNT(*) FROM chat_messages
                WHERE user_id = :user_id AND session_id = :session_id
            """),
            {"user_id": user_id, "session_id": session_id}
        )
        return result.scalar()
    finally:
        db.close()