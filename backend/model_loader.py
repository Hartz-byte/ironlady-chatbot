import os
from typing import Dict
from llama_cpp import Llama

MODEL_PATH = "../../../local_models/mistral-7b-instruct/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

MODEL_CONFIG = {
    "model_path": MODEL_PATH,
    "n_ctx": 2048,
    "n_threads": 4,
    "n_gpu_layers": 30,
    "temperature": 0.2,
    "max_tokens": 256,
    "top_p": 0.95,
    "repeat_penalty": 1.1
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
    def __init__(self, config: Dict = MODEL_CONFIG):
        self.config = config
        print(f"Loading local model from: {config['model_path']}")
        self.llm = Llama(**config)

    def generate(self, user_message: str, max_tokens: int = 256) -> str:
        prompt = PROMPT_TEMPLATE.format(
            system_prompt=_system_prompt.strip(),
            company_context=COMPANY_CONTEXT.strip(),
            user_message=user_message.strip()
        )
        # llama-cpp-python create API
        result = self.llm.create(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.2,
            top_p=0.95
        )
        text = ""
        # extract model text (llama-cpp-python returns choices)
        if "choices" in result and len(result["choices"]) > 0:
            text = result["choices"][0].get("text", "").strip()
        else:
            # some versions return 'generated_text' in a list
            text = result.get("generated_text", "")
        return text
