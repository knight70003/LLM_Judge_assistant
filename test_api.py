import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

key = os.getenv("GROQ_API_KEY")

print("Key:", key[:5])
print("Length:", len(key))

client = genai.Client(api_key=key)

response = client.models.generate_content(
    model="openai/gpt-oss-120b",
    contents="Hello"
)

print(response.text)


