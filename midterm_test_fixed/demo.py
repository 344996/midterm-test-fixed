"""Demo script to showcase the LangChain application features."""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mock_tools import FakeWeatherSearchTool, FakeCalculatorTool, FakeNewsSearchTool
from router import ConversationRouter


def run_mock_demo():
    """Fallback demo when no API key is provided (no LLM).
    Uses simple keyword heuristics to call mock tools directly.
    """
    tools = {
        "weather_search": FakeWeatherSearchTool(),
        "calculator": FakeCalculatorTool(),
        "news_search": FakeNewsSearchTool(),
    }

    demo_queries = [
        "What's the weather like in Tokyo?",
        "Calculate 5 * 3",
        "Find me news about machine learning",
        "Hello! How are you doing today?",
    ]

    print("\n🎯 Running mock demo queries (no API key)...")
    for i, query in enumerate(demo_queries, 1):
        print(f"\n--- Demo {i} ---")
        print(f"Query: {query}")
        q = query.lower()
        if "weather" in q:
            print(tools["weather_search"]._run("Tokyo"))
        elif "calculate" in q or any(op in q for op in ["+", "-", "*", "/"]):
            print(tools["calculator"]._run("5 * 3"))
        elif "news" in q:
            print(tools["news_search"]._run("machine learning"))
        else:
            print("Hi! I'm running in mock mode and can chat lightly without tools.")


def run_demo():
    """Run a demonstration of the application features."""
    print("🚀 LangChain Application Demo")
    print("=" * 40)

    # Load environment variables
    load_dotenv()

    # Check if API key is available
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  No Google API key found. Using mock responses for demo.")
        run_mock_demo()
        return

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    # Initialize tools
    tools = [
        FakeWeatherSearchTool(),
        FakeCalculatorTool(),
        FakeNewsSearchTool(),
    ]

    # Initialize router (pass tools!) 
    router = ConversationRouter(llm, tools)

    # Demo queries
    demo_queries = [
        "What's the weather like in Tokyo?",
        "Calculate 5 * 3",
        "Find me news about machine learning",
        "Hello! How are you doing today?",
    ]

    print("\n🎯 Running demo queries...")

    for i, query in enumerate(demo_queries, 1):
        print(f"\n--- Demo {i} ---")
        print(f"Query: {query}")
        try:
            response = router.process_message(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_demo()
