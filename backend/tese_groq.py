import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ No API key found in .env")
    exit()

client = Groq(api_key=api_key)

# Try to list models
try:
    models = client.models.list()
    print("✅ Available models:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"❌ Error: {e}")