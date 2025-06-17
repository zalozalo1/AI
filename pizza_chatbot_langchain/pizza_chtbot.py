
import os
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory 
from langchain_core.runnables.history import RunnableWithMessageHistory

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt


console = Console()
store = {}

def setup_environment():
    """Loads environment variables and returns the Gemini API key.
    
    Make sure you have a .env file with GOOGLE_API_KEY="your_api_key"
    Also, ensure you have the required packages:
    pip install langchain langchain-google-genai langchain-community python-dotenv rich
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print("[bold red]Error: GOOGLE_API_KEY not found in .env file.[/bold red]")
        exit()
    return api_key

def get_session_history(session_id: str) -> ChatMessageHistory:
    """Gets the chat history for a given session ID."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def display_welcome_message():
    """Displays a stylized welcome message."""
    
    welcome_panel = Panel(
        Text("Welcome to Zalo!", justify="center", style="bold magenta"),
        title="[bold green]Chatbot Ordering System[/bold green]",
        subtitle="[cyan]Type 'quit' or 'exit' to end.[/cyan]",
        border_style="green"
    )
    console.print(welcome_panel)

def display_menu():
    """Displays the pizza and drinks menu in a formatted table."""
    menu_table = Table(title="[bold cyan]Our Menu[/bold cyan]", show_header=True, header_style="bold blue")
    menu_table.add_column("Category", style="bold green", width=12)
    menu_table.add_column("Item", style="dim")
    menu_table.add_column("Details / Price", style="yellow")

    menu_table.add_row("Size", "Small, Medium, Large", "$8 / $10 / $12")
    menu_table.add_section()
    menu_table.add_row("Crust", "Thin, Thick, Stuffed", "Stuffed: +$2.50")
    menu_table.add_section()
    menu_table.add_row("Toppings", "Pepperoni, Mushrooms, Onions, Olives, Bell Peppers, Extra Cheese", "$1.00 each")
    menu_table.add_section()
    menu_table.add_row("Drinks", "Coke, Pepsi, Water", "$2.00 each")

    console.print(menu_table)

def display_final_order(order_details):
    """Displays the final confirmed order in a simple, clean text block inside a panel."""
    size = order_details.get('size', 'N/A')
    crust = order_details.get('crust', 'N/A')
    toppings_list = order_details.get('toppings', [])
    toppings = ', '.join(toppings_list) if toppings_list else "None"
    drinks_list = order_details.get('drinks', [])
    drinks = ', '.join(drinks_list) if drinks_list else "None"

    order_summary = (
        f"[bold]Size:[/bold] {size}\n"
        f"[bold]Crust:[/bold] {crust}\n"
        f"[bold]Toppings:[/bold] {toppings}\n"
        f"[bold]Drinks:[/bold] {drinks}"
    )

    order_panel = Panel(
        order_summary,
        title="[bold yellow]Your Final Order[/bold yellow]",
        border_style="yellow",
        expand=False
    )
    console.print(order_panel)


def create_chatbot_chain(api_key):
    """Configures and returns a modern, runnable LangChain chain."""
    

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a friendly and helpful ordering chatbot for a pizzeria named "Zalo".
        Your goal is to take a customer's order for pizza and drinks.
        
        Follow these steps precisely:
        1. Greet the user and ask what they would like to order.
        2. Ask for the pizza size (Small, Medium, Large).
        3. Ask for the crust type (Thin, Thick, Stuffed).
        4. Ask for toppings. The user can list multiple toppings.
        5. After getting pizza details, ask if they want any drinks (Coke, Pepsi, Water).
        6. After getting all details, confirm the complete order (pizza and drinks) with the user.
        7. Once the user confirms the order is correct, you MUST present the final order
           in a structured JSON format within a special block. THIS IS VERY IMPORTANT.
           The format MUST be:
           
           <ORDER>
           {{
             "size": "...",
             "crust": "...",
             "toppings": ["...", "..."],
             "drinks": ["...", "..."]
           }}
           </ORDER>"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    
    runnable = prompt | llm
    
    chain_with_history = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    return chain_with_history


def start_chat():
    """The main function to run the chatbot application."""
    api_key = setup_environment()
    chatbot_chain = create_chatbot_chain(api_key)
    
    display_welcome_message()
    display_menu()

    console.print("\n[bold cyan]Hello! I'm ready to take your order.[/bold cyan]")

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
            
            if user_input.lower() in ["quit", "exit"]:
                console.print("[bold magenta]Thank you for visiting Zalo. Goodbye![/bold magenta]")
                break
            
            config = {"configurable": {"session_id": "main_session"}}
            response = chatbot_chain.invoke({"input": user_input}, config=config)
            bot_response = response.content

            if "<ORDER>" in bot_response and "</ORDER>" in bot_response:
                start_tag = "<ORDER>"
                end_tag = "</ORDER>"
                json_str = bot_response[bot_response.find(start_tag)+len(start_tag) : bot_response.find(end_tag)].strip()
                
                try:
                    order_details = json.loads(json_str)
                    
                    console.print("\n[bold yellow]Great! Here is a summary of your confirmed order:[/bold yellow]")
                    display_final_order(order_details)
                    console.print("[bold magenta]\nThank you! Your order has been placed and will be ready soon.[/bold magenta]")
                    break
                except json.JSONDecodeError:
                    console.print("[bold red]Sorry, there was an error confirming your order. Let's try again.[/bold red]")
                    clean_response = bot_response.replace("<ORDER>", "").replace("</ORDER>", "").strip()
                    console.print(f"[bold cyan]PizzaBot[/bold cyan]: {clean_response}")
            else:
                console.print(f"[bold cyan]PizzaBot[/bold cyan]: {bot_response}")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold magenta]Chat ended. Goodbye![/bold magenta]")
            break

if __name__ == "__main__":
    start_chat()