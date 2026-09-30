from langchain_google_genai import ChatGoogleGenerativeAI
from conversation_db import save_summary, get_summary
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    project=os.getenv("GOOGLE_CLOUD_PROJECT")
)


def extract_text(content):
    """Gemini sometimes returns a string, sometimes a list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts).strip()
    return str(content)


def create_summary(messages):
    """Fresh summary from scratch — used for the FIRST summary of a session."""
    conversation = "\n".join(
        f"{role}:{message}"
        for role, message in messages
    )
    prompt = f"""
summarise the following conversation.
keep only information useful for
continuing the conversation.
conversation:
{conversation}
summary:
"""
    response = llm.invoke(prompt)
    return extract_text(response.content)


def update_summary(old_summary, new_messages):
    """Incremental summary — merges old summary + new turns. Cheaper than re-summarizing everything."""
    conversation = "\n".join(
        f"{role}:{message}"
        for role, message in new_messages
    )
    prompt = f"""
Existing summary of the conversation so far:
{old_summary}

New conversation turns since then:
{conversation}

Update the summary to include any new important information
(facts about the user, goals, preferences, decisions made).
Keep it concise. Do not repeat information already covered unless it changed.
Return only the updated summary text.
"""
    response = llm.invoke(prompt)
    return extract_text(response.content)


def create_and_save_summary(user_id, session_id, messages):
    """Called on a schedule (e.g. every N turns). Picks incremental vs fresh automatically."""
    old_summary = get_summary(user_id, session_id)

    if old_summary:
        summary = update_summary(old_summary, messages)
    else:
        summary = create_summary(messages)

    save_summary(user_id=user_id, session_id=session_id, summary=summary)
    return summary


if __name__ == "__main__":
    sample_messages = [
        ("user", "my name is gopi, I am learning agentic ai"),
        ("assistant", "Nice to meet you Gopi! Agentic AI is a great field."),
        ("user", "my goal is to become an agentic developer"),
    ]
    summary = create_and_save_summary(
        user_id="user_101",
        session_id="session_001",
        messages=sample_messages
    )
    print("Saved summary:", summary)