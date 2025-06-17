# Pizza Ordering Chatbot

A simple, interactive command-line chatbot for ordering pizza. This application uses a Large Language Model (LLM) to have a natural conversation with the user, guide them through the menu, and confirm their order.

## Core Technologies Used

This script is built with a modern Python stack focused on creating AI-powered applications with a great user interface.

*   **Python**: The core programming language.
*   **LangChain**: The primary framework used to build the chatbot's logic. It helps "chain" together the Language Model with prompts and chat history.
    *   `langchain-google-genai`: The specific LangChain integration package to connect to Google's AI models.
    *   `langchain-community`: Provides community-maintained integrations, such as the in-memory `ChatMessageHistory`.
    *   `langchain-core`: Contains the fundamental abstractions of LangChain, like `ChatPromptTemplate` and `RunnableWithMessageHistory`.
*   **Google Gemini**: The Large Language Model (LLM) from Google that powers the chatbot's conversational abilities.
*   **Rich**: A Python library for creating a beautiful and clean user interface in the terminal. It is used for:
    *   Displaying colored and styled text.
    *   Rendering panels, tables, and prompts.
*   **python-dotenv**: A utility for managing environment variables. It is used to securely load the `GOOGLE_API_KEY` from a `.env` file without hardcoding it into the script.

## Setup and Installation

1.  **Clone the repository or download the script.**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install langchain langchain-google-genai langchain-community python-dotenv rich
    ```

4.  **Create an environment file:**
    Create a file named `.env` in the same directory as the script and add your Google API key to it:
    ```
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
    ```

## How to Run

Execute the script from your terminal:

```bash
python pizza_bot.py
```