from langchain_core.messages import SystemMessage
from getmemory_db import memories

def format_memories(memories):
    if not memories:
        return "no stored memories."
    return "\n".join(
        f"-{memory['key']}:{memory['value']}"
        for memory in memories
    )
memory_text=format_memories(memories)
system_message=SystemMessage("""
Your are a helpful AI assistant.
here are some longterm memories about the  the user:
{memory_text}
Use this memories only when they are relevent to the current conversation.
Do not menction that you have a memory system unless user asks about it.
""")