import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from .model_loader import LocalModel

app = FastAPI(title="Iron Lady Chatbot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load FAQ file
BASE_DIR = os.path.dirname(__file__)
FAQ_PATH = os.path.join(BASE_DIR, "faqs.json")
with open(FAQ_PATH, "r", encoding="utf-8") as f:
    FAQS = json.load(f)

# Global model instance
MODEL = None

class ChatRequest(BaseModel):
    question: str
    use_model: bool = True

def init_model():
    """Initialize the local LLM model."""
    global MODEL
    if MODEL is None:
        try:
            MODEL = LocalModel()
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise
    return MODEL

def find_faq_answer(question: str) -> Optional[str]:
    """Search for a matching FAQ and return the answer if found.
    
    Args:
        question: The user's input question
        
    Returns:
        str: The answer if a match is found, None otherwise
    """
    if not question or not question.strip():
        return None
        
    question_lower = question.lower().strip()
    
    # Check for exact match first (case insensitive)
    if question_lower in FAQS:
        return FAQS[question_lower]
    
    # Check for very close matches (all words from FAQ question are in the user's question)
    for q, a in FAQS.items():
        # Skip very short FAQ questions to avoid false positives
        if len(q.split()) < 3 and q not in question_lower:
            continue
            
        # Check if all words from the FAQ question are in the user's question
        all_words_match = all(word in question_lower for word in q.split())
        
        # Also check if the FAQ question is a substring of the user's question
        is_substring = q in question_lower
        
        if all_words_match or is_substring:
            return a
    
    return None

@app.get("/")
async def root():
    return {
        "message": "Welcome to Iron Lady Chatbot API",
        "endpoints": {
            "chat": "/chat (POST)",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.post("/chat", response_model=Dict[str, Any])
async def chat(chat_request: ChatRequest):
    """
    Handle chat requests. First checks FAQs, then falls back to LLM if enabled.
    
    The function follows these steps:
    1. Validates the input
    2. Tries to find an exact or very close match in FAQs
    3. If no FAQ match and LLM is enabled, generates a response using the local LLM
    4. Returns appropriate responses with source information
    """
    try:
        user_input = chat_request.question.strip()
        
        if not user_input:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # 1) Check FAQ bank first with strict matching
        faq_answer = find_faq_answer(user_input)
        if faq_answer is not None:
            return {
                "source": "faq",
                "answer": faq_answer,
                "success": True,
                "is_faq": True
            }
        
        # 2) If no FAQ match and model usage is allowed, use the LLM
        if chat_request.use_model:
            try:
                model = init_model()
                if model is None:
                    raise Exception("Model failed to initialize")
                
                # Add context to the user's question for better LLM responses
                llm_prompt = f"""You are a helpful assistant for Iron Lady, a leadership development organization for women. 
                The user asked: {user_input}
                
                Please provide a helpful and concise response. If the question is about Iron Lady programs, 
                focus on leadership development for women. Be friendly and professional in your response."""
                
                response = model.generate(llm_prompt, max_tokens=256)
                return {
                    "source": "llm",
                    "answer": response,
                    "success": True,
                    "is_faq": False
                }
            except Exception as e:
                print(f"Error generating response: {str(e)}")
                return {
                    "source": "error",
                    "answer": "I'm having trouble generating a response right now. Please try again later.",
                    "success": False,
                    "is_faq": False
                }
        
        # 3) No FAQ match and model not used
        return {
            "source": "none",
            "answer": "I couldn't find an exact match for your question in our FAQ. Would you like me to try generating a response using our AI model?",
            "success": True,
            "is_faq": False
        }
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
