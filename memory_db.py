
from sqlalchemy import text

from database import SessionLocal
from logger_config import get_logger


logger = get_logger("memory_db")

MAX_VALUES_PER_KEY = 5


def save_memory(user_id, key, value):
    """Saves a memory value for a user.

    If a memory already exists for the given user and key, the new value is
    added only when it does not already exist. The number of stored values
    is limited to MAX_VALUES_PER_KEY, keeping the most recent values.

    Args:
        user_id: Unique identifier of the user.
        key: Memory key used to categorize the stored information.
        value: Memory value to store.

    Raises:
        Exception: Re-raises any database exception after rolling back
            the current transaction.
    """
    db = SessionLocal()

    try:
        existing_row = db.execute(
            text("""
                SELECT memory_value FROM user_memories
                WHERE user_id = :user_id AND memory_key = :key
                FOR UPDATE
            """),
            {
                "user_id": user_id,
                "key": key,
            },
        ).fetchone()

        existing = existing_row[0] if existing_row else None

        if existing:
            items = [v.strip() for v in existing.split(",")]

            if value.strip().lower() not in [item.lower() for item in items]:
                items.append(value.strip())

            items = items[-MAX_VALUES_PER_KEY:]
            merged_value = ", ".join(items)

        else:
            merged_value = value.strip()

        db.execute(
            text("""
                INSERT INTO user_memories(
                    user_id,
                    memory_key,
                    memory_value
                )
                VALUES(
                    :user_id,
                    :key,
                    :value
                )
                ON CONFLICT(user_id, memory_key)
                DO UPDATE SET
                    memory_value = EXCLUDED.memory_value,
                    updated_at = CURRENT_TIMESTAMP
            """),
            {
                "user_id": user_id,
                "key": key,
                "value": merged_value,
            },
        )

        db.commit()

    except Exception:
        db.rollback()

        logger.exception(
            f"save_memory failed | user={user_id} key={key}"
        )

        raise

    finally:
        db.close()

