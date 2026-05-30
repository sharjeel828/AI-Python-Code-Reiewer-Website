import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_groq():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment.")
        return

    client = Groq(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Hello, can you hear me?"}
            ],
        )
        print("Groq Response:", completion.choices[0].message.content)
    except Exception as e:
        print("Groq Error:", str(e))

if __name__ == "__main__":
    test_groq()
