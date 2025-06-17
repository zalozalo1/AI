import os
import time
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv
from typing import List, Dict, Any, Callable

from dataclasses import dataclass, field

from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai


@dataclass
class Config:
    """Holds all the configuration for the chatbot."""
    pinecone_api_key: str = field(init=False)
    pinecone_env: str = field(init=False)
    google_api_key: str = field(init=False)

    pinecone_index_name: str = "book-recommender-v3"
    model_dimension: int = 768

    embedding_model: str = "models/embedding-001"
    generative_model: str = "gemini-1.5-flash-latest"

    data_file: str = "books.csv"
    indexed_flag_file: str = "pinecone_index_v3_complete.flag"
    
    rows_to_process: int = 100

    def __post_init__(self):
        """Load environment variables after the object is created."""
        load_dotenv()
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

        if not all([self.pinecone_api_key, self.pinecone_env, self.google_api_key]):
            raise ValueError("One or more required API keys are missing from the .env file.")


class GeminiService:
    """Handles all interactions with the Google Gemini API."""
    def __init__(self, api_key: str, embedding_model: str, generative_model: str):
        genai.configure(api_key=api_key)
        self.embedding_model = embedding_model
        self.generative_model = genai.GenerativeModel(generative_model)
        print("✅ Gemini Service Initialized")

    def embed_content(self, texts: List[str], task_type: str) -> List[List[float]]:
        """Generates embeddings for a list of texts."""
        result = genai.embed_content(
            model=self.embedding_model,
            content=texts,
            task_type=task_type
        )
        return result['embedding']

    def generate_response(self, prompt: str) -> str:
        """Generates a text response from a prompt."""
        try:
            response = self.generative_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Sorry, I encountered an error while generating a response: {e}"


class PineconeService:
    """Manages all Pinecone operations."""
    def __init__(self, api_key: str, environment: str):
        self.pc = Pinecone(api_key=api_key)
        print("✅ Pinecone Service Initialized")

    def get_or_create_index(self, name: str, dimension: int) -> Pinecone.Index:
        """Gets a Pinecone index, creating it if it doesn't exist."""
        if name not in self.pc.list_indexes().names():
            print(f"Creating new Pinecone index: {name}...")
            self.pc.create_index(
                name=name, dimension=dimension, metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            while not self.pc.describe_index(name).status['ready']:
                time.sleep(1)
            print("Index created successfully.")
        else:
            print(f"Index '{name}' already exists.")
        return self.pc.Index(name)

    def upsert_data(self, index: Pinecone.Index, data: pd.DataFrame, embed_function: Callable):
        """Embeds and upserts data into the Pinecone index in batches."""
        print("Embedding and upserting data to Pinecone...")
        batch_size = 50
        for i in tqdm(range(0, len(data), batch_size), desc="Upserting to Pinecone"):
            batch_df = data.iloc[i:i + batch_size]
            texts = batch_df['description_for_embedding'].tolist()
            
            embeddings = embed_function(texts, "RETRIEVAL_DOCUMENT")
            
            vectors = []
            for idx, row in batch_df.iterrows():
                vector = {
                    "id": row['bookID'],
                    "values": embeddings[len(vectors)],
                    "metadata": {
                        "title": row['title'],
                        "authors": row['authors'],
                        "average_rating": float(row['average_rating'])
                    }
                }
                vectors.append(vector)
            index.upsert(vectors=vectors)
        print("Upsert complete.")


class BookChatbot:
    """The main chatbot application orchestrator."""
    def __init__(self, config: Config):
        self.config = config
        self.gemini = GeminiService(config.google_api_key, config.embedding_model, config.generative_model)
        self.pinecone = PineconeService(config.pinecone_api_key, config.pinecone_env)
        self.data = self._load_data()
        self.index = self.pinecone.get_or_create_index(config.pinecone_index_name, config.model_dimension)

    def _load_data(self) -> pd.DataFrame:
        """Loads and prepares the book data from the CSV file."""
        print("Loading and preparing data...")
        try:
            df = pd.read_csv(self.config.data_file, on_bad_lines='skip')
        except FileNotFoundError:
            print(f"Fatal Error: The file '{self.config.data_file}' was not found.")
            exit()
            
        df.dropna(subset=['bookID', 'title', 'authors'], inplace=True)
        df = df.head(self.config.rows_to_process)
        df['description_for_embedding'] = "Title: " + df['title'] + "; Authors: " + df['authors']
        df['bookID'] = df['bookID'].astype(str)
        
        print(f"Data loaded. Processing {len(df)} books.")
        return df

    def _format_context(self, matches: List[Dict[str, Any]]) -> str:
        """Formats the retrieved book data into a string for the generative model."""
        context = "Based on the user's request, here are some potentially relevant books from our database:\n\n"
        for i, match in enumerate(matches):
            metadata = match.get('metadata', {})
            context += f"Result {i+1}:\n"
            context += f"- Title: {metadata.get('title', 'N/A')}\n"
            context += f"- Authors: {metadata.get('authors', 'N/A')}\n"
            context += f"- Average Rating: {metadata.get('average_rating', 'N/A')}\n\n"
        return context
    
    def setup(self):
        """Checks if data needs to be indexed and performs the operation if so."""
        if not os.path.exists(self.config.indexed_flag_file):
            print("First-time setup: Indexing data. This may take a moment...")
            self.pinecone.upsert_data(self.index, self.data, self.gemini.embed_content)
            with open(self.config.indexed_flag_file, "w") as f:
                f.write("done")
            print("Setup complete.")
        else:
            print("Data already indexed. Ready to chat.")

    def run(self):
        """Starts the main interactive chat loop."""
        print("\n--- Book Recommender Chatbot ---")
        print("Ask me for book recommendations! Type 'quit' or 'exit' to stop.")

        while True:
            user_query = input("\nYou: ")
            if user_query.lower() in ['quit', 'exit']:
                print("Bot: Goodbye!")
                break

            query_embedding = self.gemini.embed_content([user_query], "RETRIEVAL_QUERY")[0]

            matches = self.index.query(vector=query_embedding, top_k=5, include_metadata=True)['matches']

            if not matches:
                print("Bot: I'm sorry, I couldn't find any relevant books. Please try a different query.")
                continue

            context = self._format_context(matches)
            
            prompt = (
                f"**Context - Relevant Books:**\n{context}\n\n"
                f"**User's Request:** \"{user_query}\"\n\n"
                "**Your Task:**\n"
                "You are a friendly and helpful bookstore assistant. Based *only* on the book results provided in the context, give a conversational recommendation to the user.\n\n"
                "**Formatting Rules:**\n"
                "1. Start with a friendly, one-sentence introduction.\n"
                "2. Present the recommended books as a bulleted list (using '*' or '-').\n"
                "3. For each book in the list, make the title **bold**.\n"
                "4. After the title, briefly explain (in 1-2 sentences) why it fits the user's request.\n"
                "5. Do not invent books or suggest any that are not in the context."
            )
            
            response = self.gemini.generate_response(prompt)
            print(f"Bot: {response}")


if __name__ == '__main__':
    try:
        config = Config()
        chatbot = BookChatbot(config)
        chatbot.setup()
        chatbot.run()
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")