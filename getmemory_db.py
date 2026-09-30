from sqlalchemy import text
from database import SessionLocal
def get_memories(user_id:str):
    db=SessionLocal()
    try:
        query=text("""
        SELECT memory_key,memory_value
        FROM user_memories
        WHERE user_id=:user_id
        ORDER BY updated_at DESC""")
        rows=db.execute(
            query,
            {"user_id":user_id}
        ).fetchall()
        memories=[]
        for row in rows:
            memories.append({
                "key":row[0],
                "value":row[1]
            })
        return memories
    finally:
        db.close()

