import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

key = os.getenv("GOOGLE_API_KEY")

print("Key:", key[:5])
print("Length:", len(key))

client = genai.Client(api_key=key)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Hello"
)

print(response.text)