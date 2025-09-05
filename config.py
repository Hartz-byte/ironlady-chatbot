# config.py
from pathlib import Path

# Path to your gguf model file - update this
MODEL_PATH = str("../../../local_models/mistral-7b-instruct/mistral-7b-instruct-v0.2.Q4_K_M.gguf")

# Llama-cpp-python generation params
LLAMA_PARAMS = {
    "n_ctx": 2048,
    "n_threads": 8,
    "n_gpu_layers": 30,
    "temperature": 0.3,
    "max_tokens": 256,
    "top_p": 0.95,
    "repeat_penalty": 1.1
}
