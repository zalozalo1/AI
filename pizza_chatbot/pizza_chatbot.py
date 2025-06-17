import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import textwrap

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: GEMINI_API_KEY not found. Please set it in your .env file.")
    exit()

genai.configure(api_key=API_KEY)


SYSTEM_PROMPT = """
You are a helpful and friendly chatbot for a pizza restaurant named "Zalo's Pizzeria".
Your primary goal is to take a customer's pizza order by guiding them through the menu options and collecting their choices.

---
ZALO'S PIZZERIA MENU
---

**1. Specialty Pizzas (Crust of your choice included):**
- **Zalo Supreme** (Pepperoni, Sausage, Green Peppers, Onions, Mushrooms)
  (S: $14.99, M: $18.99, L: $22.99)
- **Meat Marvel** (Pepperoni, Sausage, Ham, Bacon)
  (S: $14.99, M: $18.99, L: $22.99)
- **Veggie Delight** (Mushrooms, Onions, Green Peppers, Black Olives, Fresh Tomatoes)
  (S: $13.99, M: $17.99, L: $21.99)
- **Classic Pepperoni** (Loaded with a double-layer of pepperoni)
  (S: $12.99, M: $15.99, L: $19.99)

**2. Build Your Own Pizza:**
- **Start with a Size (includes cheese, sauce, and your choice of crust):**
  - Small (10"): $10.99
  - Medium (12"): $13.99
  - Large (14"): $16.99
- **Choose a Crust:**
  - Thin Crust
  - Hand-Tossed
  - Deep Dish (+$2.00)
  - Stuffed Crust (+$3.00)
- **Add Toppings (+$1.50 each for M/L, +$1.00 for S):**
  - Meats: Pepperoni, Sausage, Ham, Bacon, Grilled Chicken
  - Veggies: Mushrooms, Onions, Green Peppers, Black Olives, Fresh Tomatoes, Spinach, Jalapenos

**3. Sides:**
- Garlic Knots (6 pcs): $5.00
- Cheesy Breadsticks: $6.00
- Wings (8 pcs - Hot or BBQ): $9.00

**4. Drinks:**
- Soda (Coke, Diet Coke, Sprite): $2.50
- Bottled Water: $2.00
---

RULES:
- Be conversational and friendly.
- **Your first question MUST be to ask if the customer wants a specialty pizza or to build their own.**
- Ask one primary question at a time.
- **PRESENTATION:** When presenting menu options, you MUST format them as a clear, bulleted list using newlines (`\\n`).
- You MUST stick to the items and prices listed on the MENU.
- When a specialty pizza is chosen, populate a `pizza_name` key in the `order_details` object, in addition to listing its ingredients under `toppings`.
- **CRITICAL PRICING RULE:** When the entire order is complete, you MUST add an `item_prices` object and a `total_price` string to the `order_details`. `item_prices` should map the full item name to its calculated price. `total_price` is the sum of all values in `item_prices`. Prices must be numbers.
- IMPORTANT: When you believe the entire order is complete, you MUST set the "status" field to "complete".
- ALWAYS respond with a JSON object with three keys: "status", "response", and "order_details".

Example (Complete order with pricing):
{
  "status": "complete",
  "response": "Perfect! I have your order for a Large Zalo Supreme on Deep Dish with a side of Wings and a Coke. I'll show you the final order with pricing now.",
  "order_details": {
    "pizza_name": "Zalo Supreme",
    "size": "Large",
    "crust": "Deep Dish",
    "toppings": ["Pepperoni", "Sausage", "Green Peppers", "Onions", "Mushrooms"],
    "sides": ["Wings (Hot)"],
    "drinks": ["Coke"],
    "item_prices": {
      "Zalo Supreme (Large)": 22.99,
      "Deep Dish Crust": 2.00,
      "Wings (Hot)": 9.00,
      "Coke": 2.50
    },
    "total_price": "36.49"
  }
}
"""

def print_bot_message(message, width=60):
    """Prints the bot's message inside a styled box."""
    lines = message.replace('\\n', '\n').split('\n')
    print(f"╭{'─' * (width-2)}╮")
    print(f"│ 🤖 {'Zalo\'s Pizzeria'.ljust(width - 6)} │")
    print(f"├{'─' * (width-2)}┤")
    for line in lines:
        wrapped_lines = textwrap.wrap(line, width - 6, drop_whitespace=False, replace_whitespace=False)
        if not wrapped_lines:
            print(f"│ {' ' * (width - 4)} │")
        for wrapped_line in wrapped_lines:
            print(f"│   {wrapped_line.ljust(width - 7)} │")
    print(f"╰{'─' * (width-2)}╯")

def get_user_input():
    """Prints a styled prompt for the user and gets input."""
    return input("   👤 You: ")

# --- MODIFIED: Toppings are now displayed in a wrapped row ---
def display_final_order(order_details):
    """Formats and prints the final order summary, including pricing."""
    width = 55
    top_border = f"╭{'─' * (width-2)}╮"
    bottom_border = f"╰{'─' * (width-2)}╯"
    separator = f"├{'─' * (width-2)}┤"

    def print_line(text, centered=False):
        if centered:
            content = text.center(width - 4)
            print(f"│ {content} │")
        else:
            print(f"│ {text.ljust(width - 4)} │")

    def print_empty_line():
        print(f"│ {' ' * (width - 4)} │")

    print("\n\n" + top_border)
    print_line("🍕 Zalo's Pizzeria 🍕", centered=True)
    print_line("~ Your Final Order ~", centered=True)
    print(separator)
    print_empty_line()

    # --- Item Details ---
    if 'pizza_name' in order_details:
        print_line(f"  PIZZA: {order_details['pizza_name']}")
    print_line(f"  • Size: {order_details.get('size', 'N/A')}")
    print_line(f"  • Crust: {order_details.get('crust', 'N/A')}")
    
    if order_details.get('toppings'):
        label = "  • Toppings: "
        toppings_str = ", ".join(order_details['toppings'])
        
        wrapped_lines = textwrap.wrap(
            label + toppings_str,
            width=width - 4, 
            subsequent_indent=' ' * len(label)
        )
        for line in wrapped_lines:
            print_line(line)

    if order_details.get('sides'):
        print_empty_line()
        print_line(f"  SIDES: {', '.join(order_details['sides'])}")
    if order_details.get('drinks'):
        print_empty_line()
        print_line(f"  DRINKS: {', '.join(order_details['drinks'])}")

    if 'item_prices' in order_details and 'total_price' in order_details:
        print_empty_line()
        print(separator)
        print_line("Price Breakdown", centered=True)
        print_empty_line()

        for item, price in order_details['item_prices'].items():
            price_str = f"${float(price):.2f}"
            dots = '.' * (width - 8 - len(item) - len(price_str))
            print_line(f"  {item} {dots} {price_str}")

        print_empty_line()
        total_price_str = f"${float(order_details['total_price']):.2f}"
        total_label = "TOTAL"
        dots = '.' * (width - 8 - len(total_label) - len(total_price_str))
        print_line(f"  {total_label} {dots} {total_price_str}")

    print_empty_line()
    print(bottom_border)
    print("      Thank you for your order! Enjoy your meal! 🎉\n")


def main():
    """The main function to run the chatbot."""
    print_bot_message("Welcome! I can help you place an order.\nType 'quit' or 'exit' anytime to end the chat.")

    model = genai.GenerativeModel('gemini-1.5-flash')

    initial_model_response = json.dumps({
        "status": "in_progress",
        "response": "Hello! Welcome to Zalo's Pizzeria. Would you like to try one of our delicious specialty pizzas, or would you prefer to build your own?",
        "order_details": {}
    })

    chat = model.start_chat(history=[
        {'role': 'user', 'parts': [SYSTEM_PROMPT]},
        {'role': 'model', 'parts': [initial_model_response]}
    ])

    initial_greeting = json.loads(initial_model_response)["response"]
    print_bot_message(initial_greeting)

    while True:
        user_input = get_user_input()

        if user_input.lower() in ['quit', 'exit', 'bye']:
            break

        try:
            response = chat.send_message(user_input)
            ai_response_text = response.text

            try:
                if ai_response_text.strip().startswith("```json"):
                    ai_response_text = ai_response_text.strip()[7:-3].strip()

                ai_data = json.loads(ai_response_text)
                bot_message = ai_data.get("response", "I'm not sure how to respond to that.")
                status = ai_data.get("status", "in_progress")
                order_details = ai_data.get("order_details", {})

                print_bot_message(bot_message)

                if status == 'complete':
                    display_final_order(order_details)

                    print_bot_message("Would you like to place another order? (yes/no)")
                    another = get_user_input()

                    if another.lower().strip() in ['yes', 'y', 'sure', 'ok', 'yeah']:
                        print_bot_message("Great! Let's start a new order.")
                        chat = model.start_chat(history=[
                            {'role': 'user', 'parts': [SYSTEM_PROMPT]},
                            {'role': 'model', 'parts': [initial_model_response]}
                        ])
                        print_bot_message(initial_greeting)
                    else:
                        break

            except json.JSONDecodeError:
                print_bot_message(f"SYSTEM: Raw response was not valid JSON.\n\n{ai_response_text}")
            except Exception as e:
                print_bot_message(f"SYSTEM: An error occurred while processing the response: {e}")

        except Exception as e:
            print_bot_message(f"SYSTEM: An error occurred with the API call: {e}")

    print_bot_message("Thank you for visiting Zalo's Pizzeria. Goodbye! 👋")

if __name__ == "__main__":
    main()