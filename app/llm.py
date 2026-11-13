import os
import requests

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def load_env():
    # read the .env file so the key stays out of the code
    path = os.path.join(BASE_FOLDER, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip())


load_env()


def ask_llm(system_prompt, user_message, temperature=0.2):
    key = os.environ.get("GROQ_API_KEY", "")
    if key == "" or key == "your_key_here":
        raise RuntimeError("GROQ_API_KEY is missing. Add it to the .env file.")

    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    body = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}

    try:
        response = requests.post(GROQ_URL, json=body, headers=headers, timeout=60)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("The LLM took too long to answer")
    except requests.exceptions.RequestException as e:
        raise RuntimeError("Could not get an answer from the LLM: " + str(e)[:120])

    return response.json()["choices"][0]["message"]["content"]
