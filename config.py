import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

JUDGE_MODEL = os.getenv("JUDGE_MODEL", "openai/gpt-oss-120b")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "openai/gpt-oss-120b")

TEMPERATURE = float(os.getenv("TEMPERATURE", 0))

MAX_OUTPUT_TOKENS = int(
    os.getenv("MAX_OUTPUT_TOKENS", 1024)
)