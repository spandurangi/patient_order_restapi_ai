import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

def extract_patient_data(text: str) -> dict:
    prompt = (
        "Extract the patient's First Name, Last Name, and Date of Birth from the following medical text.\n"
        "Return only a valid JSON object and nothing else.\n"
        "Do not include any explanation, summary, or extra text.\n\n"
        "Format:\n"
        "{ \"first_name\": \"...\", \"last_name\": \"...\", \"date_of_birth\": \"...\" }\n\n"
        f"Text:\n{text}"
    )

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a medical document parser."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.3
    }

    response = requests.post(TOGETHER_API_URL, headers=HEADERS, json=body)

    if response.status_code != 200:
        raise ValueError(f"Together.ai request failed: {response.status_code} {response.text}")

    content = response.json()["choices"][0]["message"]["content"]
    print(content)

    try:
        import json
        return json.loads(content)
    except:
        return {"first_name": None, "last_name": None, "date_of_birth": None, "raw_response": content}
