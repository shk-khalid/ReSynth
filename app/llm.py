import os
import time
from openai import OpenAI
import ollama
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "poolside/laguna-m.1:free")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower().strip() # "openrouter" or "ollama"

# Initialize standard OpenAI client pointing to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def call_with_retry(api_func, max_retries: int = 5, base_delay: float = 2.0):
    """Executes a function and retries with dynamic / exponential backoff if a rate limit (429) occurs."""
    for attempt in range(max_retries):
        try:
            return api_func()
        except Exception as e:
            err_str = str(e).lower()
            is_rate_limit = "rate_limit" in err_str or "429" in err_str or "rate limit" in err_str
            
            if is_rate_limit and attempt < max_retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                
                # Check for dynamic retry-after value from OpenRouter error metadata
                if hasattr(e, "body") and isinstance(e.body, dict):
                    err_data = e.body.get("error", {})
                    if isinstance(err_data, dict):
                        metadata = err_data.get("metadata", {})
                        if isinstance(metadata, dict):
                            retry_after = metadata.get("retry_after_seconds")
                            if retry_after is not None:
                                try:
                                    sleep_time = float(retry_after) + 1.0  # Add 1 second buffer
                                    print(f"OpenRouter requested dynamic retry after {retry_after}s.")
                                except (ValueError, TypeError):
                                    pass
                
                print(f"Rate limited (429) by OpenRouter. Retrying in {sleep_time:.1f}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(sleep_time)
                continue
            raise e

def _generate_openrouter(prompt: str) -> str:
    def _call():
        return client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a structured research synthesizer. Use only the provided facts. Do not invent information."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )
    response = call_with_retry(_call)
    return response.choices[0].message.content

def _generate_json_openrouter(prompt: str) -> str:
    def _call():
        return client.chat.completions.create(
            model=LLM_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a structured research planner/validator. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )
    response = call_with_retry(_call)
    return response.choices[0].message.content

def _generate_ollama(prompt: str) -> str:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a structured research synthesizer. Use only the provided facts. Do not invent information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.2,
            "num_ctx": 4096,
        }
    )
    return response["message"]["content"]

def _generate_json_ollama(prompt: str) -> str:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a structured research planner. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json",
        options={
            "temperature": 0.2,
            "num_ctx": 4096,
        }
    )
    return response["message"]["content"]

def generate(prompt: str) -> str:
    if LLM_PROVIDER == "ollama":
        print(f"Using Ollama ({OLLAMA_MODEL}) as explicitly configured.")
        return _generate_ollama(prompt)
        
    if OPENROUTER_API_KEY:
        try:
            print(f"Trying OpenRouter ({LLM_MODEL})...")
            return _generate_openrouter(prompt)
        except Exception as e:
            print(f"OpenRouter generation failed: {e}. Falling back to Ollama...")
            return _generate_ollama(prompt)
    else:
        print("OPENROUTER_API_KEY not found. Falling back to Ollama...")
        return _generate_ollama(prompt)

def generate_json(prompt: str) -> str:
    if LLM_PROVIDER == "ollama":
        print(f"Using Ollama ({OLLAMA_MODEL}) as explicitly configured for JSON.")
        return _generate_json_ollama(prompt)
        
    if OPENROUTER_API_KEY:
        try:
            print(f"Trying OpenRouter ({LLM_MODEL}) for JSON...")
            return _generate_json_openrouter(prompt)
        except Exception as e:
            print(f"OpenRouter JSON generation failed: {e}. Falling back to Ollama...")
            return _generate_json_ollama(prompt)
    else:
        print("OPENROUTER_API_KEY not found. Falling back to Ollama...")
        return _generate_json_ollama(prompt)