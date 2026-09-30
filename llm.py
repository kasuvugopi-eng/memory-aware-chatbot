

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import BaseChatModel
import os
from dotenv import load_dotenv

load_dotenv()

def get_model() -> BaseChatModel:
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
        project=os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    return model