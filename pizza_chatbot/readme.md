# Zalo's Pizzeria AI Chatbot

This is a command-line pizza ordering chatbot powered by the Google Gemini API. It simulates a conversation with a pizzeria chatbot to take a user's order, tracks all items, and provides a final, priced summary.

## Features

- **Conversational Ordering**: Engages the user in a natural, friendly conversation.
- **Dynamic Menu Navigation**: Handles both specialty pizzas and custom "build-your-own" orders.
- **Order Management**: Accurately tracks choices for pizza size, crust, toppings, sides, and drinks.
- **Automatic Pricing**: Calculates the price for each item and the total order cost upon completion.
- **Styled CLI**: Presents the bot's messages and the final order summary in a clean, formatted interface.

## ⚙️ Setup and Installation

### 1. Prerequisites

- Python 3.7+
- A Google Gemini API Key. You can get one from [Google AI Studio](https://aistudio.google.com/).

### 2. Install Dependencies

1.  Save the script in a project folder. Let's call the script `chatbot.py`.

2.  Create a file named `requirements.txt` in the same folder with the following content:
    ```
    google-generativeai
    python-dotenv
    ```

3.  Open your terminal in the project folder and install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Set Up Your API Key

1.  In the same project folder, create a file named `.env`.

2.  Add your Gemini API key to the `.env` file like this. **Do not use quotes.**

    ```env
    GEMINI_API_KEY=YOUR_API_KEY_HERE
    ```
    (Replace `YOUR_API_KEY_HERE` with your actual key).

## 🚀 How to Run

Once setup is complete, run the script from your terminal:

```bash
python chatbot.py