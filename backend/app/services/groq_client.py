from groq import Groq
from app.config import Config

_client = None

def get_groq_client():
    global _client
    if _client is None:
        _client = Groq(api_key=Config.GROQ_API_KEY)
    return _client

def call_groq(prompt: str, temperature: float = 0.1, max_tokens: int = 200) -> str:
    """
    Sends a single prompt to Groq's LLaMA 3.3 70B and returns the raw text response.
    Low temperature keeps reflection-token outputs consistent (per PRD risk mitigation).
    """
    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()