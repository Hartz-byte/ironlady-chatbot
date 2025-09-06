# Iron Lady Chatbot

A conversational AI assistant for the Iron Lady leadership programs, providing information about courses, mentors, and program details through a user-friendly chat interface.

## Features

- 🤖 Interactive chat interface with a modern, responsive design
- 🔍 FAQ-based responses for quick information retrieval
- 🧠 Integration with Mistral-7B-Instruct model for advanced query handling
- ⚡ FastAPI backend with efficient model loading
- 📱 Mobile-responsive frontend built with Streamlit
- 🔄 Real-time chat with message history
- 🕒 Timestamped messages with 12-hour format

## Project Structure

```
ironlady-chatbot/
├── backend/                 # FastAPI backend
│   ├── __init__.py
│   ├── app.py              # Main FastAPI application
│   ├── model_loader.py     # Model loading and inference
│   └── static/             # Static files (favicon, etc.)
├── frontend/               # Streamlit frontend
│   ├── __init__.py
│   └── streamlit_app.py    # Main Streamlit application
├── config.py               # Configuration settings
└── requirements.txt        # Python dependencies
```

## Prerequisites

- Python 3.10+
- pip (Python package manager)
- CUDA-compatible GPU (recommended) or CPU
- At least 8GB RAM (16GB+ recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ironlady-chatbot.git
   cd ironlady-chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install llama-cpp-python with GPU support (recommended):
   ```bash
   CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
   ```

## Running the Application

### Backend

Start the FastAPI server:
```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Frontend

In a new terminal, start the Streamlit app:
```bash
cd frontend
streamlit run streamlit_app.py
```

The chat interface will be available at `http://localhost:8501`

## Configuration

Update the following in `config.py` as needed:
- Model path
- API endpoints
- Model parameters (temperature, max tokens, etc.)

## Environment Variables

Create a `.env` file in the project root:
```
API_BASE_URL=http://localhost:8000
```

## Usage

1. Open the Streamlit frontend in your web browser
2. Type your questions about Iron Lady programs
3. The bot will respond with relevant information from FAQs or generate a response using the AI model

## FAQ

Common questions are pre-programmed in `backend/faqs.json`. The bot will first try to match user queries against these FAQs before using the AI model.

## Troubleshooting

- **Model loading issues**: Ensure you have enough system resources and the correct CUDA version installed
- **API connection errors**: Verify both backend and frontend servers are running
- **Performance issues**: Consider reducing the model size or using a GPU for better performance

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgements

- [Mistral AI](https://mistral.ai/) for the Mistral-7B-Instruct model
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Streamlit](https://streamlit.io/) for the frontend interface
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for model inference