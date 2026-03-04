from click import option
import ollama

def generate(prompt: str):
    response = ollama.chat(
        model="mistral",
        messages = [
            {
                "role": "system",
                "content": "You are a structured research synthesizer. Use only the provided facts. Do not invent information",
            },
            {
                "role": "user",
                "content": prompt
            }
        ], 
        options = {
            "temperature": 0.2,      # randomness (lower = more deterministic)
            "num_thread": 4,         # CPU threads used
            "num_predict": 800,      # max tokens generated
            "top_k": 40,             # limits token choices
            "top_p": 0.9,            # probability sampling limit
            "repeat_penalty": 1.1,   # reduces repetition
            "repeat_last_n": 64,     # tokens checked for repetition
            "num_ctx": 4096,         # context window size
            "num_batch": 256,        # tokens processed per batch
            "num_gpu": 1,            # GPUs used
            "num_gpu_layers": 10,    # layers offloaded to GPU
        }
    )
    return response["message"]["content"]

def generate_json(prompt: str):
    response = ollama.chat(
        model="mistral",
        messages = [
            {
                "role": "system",
                "content": "You are a structured research planner. Always respond with valid JSON only.",
            },
            {
                "role": "user",
                "content": prompt
            }
        ], 
        format="json",
        options = {
            "temperature": 0.2,      # randomness (lower = more deterministic)
            "num_thread": 4,         # CPU threads used
            "num_predict": 800,      # max tokens generated
            "top_k": 40,             # limits token choices
            "top_p": 0.9,            # probability sampling limit
            "repeat_penalty": 1.1,   # reduces repetition
            "repeat_last_n": 64,     # tokens checked for repetition
            "num_ctx": 4096,         # context window size
            "num_batch": 256,        # tokens processed per batch
            "num_gpu": 1,            # GPUs used
            "num_gpu_layers": 10,    # layers offloaded to GPU
        }
    )
    return response["message"]["content"]