import os
import fcntl
from typing import Dict
from llama_cpp import Llama

# mistral-7b-instruct model path
MODEL_PATH = "../../../local_models/mistral-7b-instruct/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

MODEL_CONFIG = {
    "model_path": MODEL_PATH,
    "n_ctx": 2048,  # Context window size
    "n_threads": 4,  # Number of CPU threads to use
    "n_gpu_layers": 30,  # Number of layers to offload to GPU
    "temperature": 0.2,  # Lower for more focused responses
    "max_tokens": 512,   # Maximum tokens to generate
    "top_p": 0.95,      # Nucleus sampling parameter
    "repeat_penalty": 1.1,  # Penalize repetition
    "n_batch": 512,     # Batch size for prompt processing
    "main_gpu": 0,      # Use first GPU
    "tensor_split": [0.9],  # Use 90% of GPU memory
    "verbose": True     # Show debug info
}

_system_prompt = """
You are IronLadyBot — a helpful, concise assistant for answering FAQs about the Iron Lady leadership programs.
Rules:
- If the user asks a question that directly relates to the FAQs (programs, duration, mode, certificates, mentors), prefer the FAQ answer.
- If you are unsure, ask a clarifying question rather than hallucinating facts.
- Keep answers brief (2-5 sentences).
- Use the provided company context exactly as factual background if needed.
"""

# Company context (seeded from website)
COMPANY_CONTEXT = """
Iron Lady delivers high-impact leadership programs for women including programs like
1-Crore Club, 100 Board Members, and the Leadership Essentials Program. Programs are
built by senior entrepreneurs and industry leaders and often run online as live cohorts,
with certification and post-program mentorship/community support.
"""

PROMPT_TEMPLATE = """SYSTEM:
{system_prompt}

CONTEXT:
{company_context}

USER:
{user_message}

INSTRUCTIONS:
Respond as a helpful assistant. If the user asks for specific program logistics (duration, online/offline, certificate, mentors), be concise and accurate and prefer FAQ answers. If not sure, ask for clarification.
"""

class LocalModel:
    _instance = None
    _lock_file = "/tmp/ironlady_model.lock"
    _initialized = False
    
    def __new__(cls, config: Dict = MODEL_CONFIG):
        if cls._instance is None:
            # Use a file lock to prevent multiple processes from loading the model
            lock_fd = os.open(cls._lock_file, os.O_CREAT | os.O_WRONLY)
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                cls._instance = super(LocalModel, cls).__new__(cls)
                cls._instance._initialize(config)
            except BlockingIOError:
                # Another process is initializing, wait for it
                fcntl.flock(lock_fd, fcntl.LOCK_SH)
                if cls._instance is None:
                    raise RuntimeError("Failed to initialize model")
            finally:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)
        return cls._instance
    
    def _initialize(self, config: Dict):
        if not self._initialized:
            self.config = config
            print(f"Loading local model from: {config['model_path']}")
            
            if not os.path.exists(config['model_path']):
                raise FileNotFoundError(f"Model file not found at {config['model_path']}")
                
            self.llm = Llama(
                model_path=config['model_path'],
                n_ctx=config['n_ctx'],
                n_threads=config['n_threads'],
                n_gpu_layers=config['n_gpu_layers'],
                n_batch=config.get('n_batch', 512),
                main_gpu=config.get('main_gpu', 0),
                tensor_split=config.get('tensor_split', [0.9]),
                verbose=config.get('verbose', True)
            )
            
            if self.llm._model is not None:
                print(f"Model loaded successfully with {config['n_gpu_layers']} layers on GPU")
            else:
                print("Warning: Model not properly initialized")
                
            self._initialized = True

    def generate(self, user_message: str, max_tokens: int = 256):
        """Generate a response using the local LLM."""
        prompt = PROMPT_TEMPLATE.format(
            system_prompt=_system_prompt,
            company_context=COMPANY_CONTEXT,
            user_message=user_message
        )
        
        try:
            # Generate response
            response = self.llm(
                prompt=prompt,
                max_tokens=min(max_tokens, self.config["max_tokens"]),
                temperature=self.config["temperature"],
                top_p=self.config["top_p"],
                repeat_penalty=self.config["repeat_penalty"],
                stop=["USER:", "\n\n"],
                echo=False
            )
            
            # Extract and clean the response
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['text'].strip()
            elif 'text' in response:
                return response['text'].strip()
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
                
        except Exception as e:
            print(f"Error in generate: {str(e)}")
            return f"I encountered an error: {str(e)}"
