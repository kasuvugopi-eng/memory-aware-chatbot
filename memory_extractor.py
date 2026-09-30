from langchain_google_genai import ChatGoogleGenerativeAI
from memory_schema import MemoryExtraction
from dotenv import load_dotenv
from memory_db import save_memory
from llm import get_model

load_dotenv()

llm = get_model()
structured_llm = llm.with_structured_output(MemoryExtraction)

ALLOWED_KEYS = [
    "name", "profession", "skills", "interests", "goals",
    "preferences", "communication_style", "location", "education"
]


def extract_memories(user_message: str):
    prompt = f"""
Extract only useful long-term information about the user from the following message.
Do not extract temporary or one-time information (e.g. "I'm tired today").

User message:
{user_message}

Use ONLY these keys when applicable (do not invent new key names):
{", ".join(ALLOWED_KEYS)}

If a fact doesn't cleanly fit any key above, skip it rather than inventing a new key.
If the message mentions multiple goals/skills/interests, combine them into one
comma-separated value under the same key (e.g. key="skills", value="Python, SQL").

Return an empty list if there is no useful long-term information.
"""
    result = structured_llm.invoke(prompt)
    return result.memories


def extract_and_save(user_id: str, user_message: str):
    memories = extract_memories(user_message)
    for memory in memories:
        save_memory(user_id=user_id, key=memory.key, value=memory.value)
        print(f"saved->{memory.key}={memory.value}")
    return memories


if __name__ == "__main__":
    memories = extract_and_save(
        user_id="user_101",
        user_message="my name is gopi. iam learning agentic ai. my goal is to become agentic developer"
    )