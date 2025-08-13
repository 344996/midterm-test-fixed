"""Demo script to showcase the LangChain application features."""

import os
from dotenv import load_dotenv
load_dotenv()
from mock_tools import FakeWeatherSearchTool, FakeCalculatorTool, FakeNewsSearchTool
from router import ConversationRouter


def run_mock_demo():
    """Fallback demo when no API key or LLM package is available."""
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

    print("\n🎯 Running mock demo queries (no API key or LLM)...")
    for i, query in enumerate(demo_queries, 1):
        print(f"\n--- Demo {i} ---")
        print(f"Query: {query}")
        q = query.lower()
        if "weather" in q:
            print(tools["weather_search"]._run("Tokyo"))
        elif "calculate" in q or any(op in q for op in ['+', '-', '*', '/']):
            import re
            m = re.search(r"(\d+\s*[\+\-\*/]\s*\d+)", q)
            expr = m.group(1) if m else '5 * 3'
            print(tools["calculator"]._run(expr))
        elif "news" in q:
            if "about" in q:
                topic = q.split('about',1)[1].strip().rstrip('? .')
            else:
                topic = 'general'
            print(tools['news_search']._run(topic))
        else:
            print("Hi! I'm running in mock mode and can chat lightly without tools.")


def run_demo():
    """Run a demonstration of the application features."""
    print("🚀 LangChain Application Demo")
    print("=" * 40)

    # Check if API key is available
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  No Google API key found. Using mock responses for demo.")
        run_mock_demo()
        return

    # Try to import LLM library only if API key present
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except Exception:
        print("⚠️  LLM package not available. Falling back to mock demo.")
        run_mock_demo()
        return

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash',
        temperature=0.7,
        google_api_key=api_key
    )

    # Initialize tools
    tools = [FakeWeatherSearchTool(), FakeCalculatorTool(), FakeNewsSearchTool()]

    # Initialize router (pass tools)
    router = ConversationRouter(llm, tools)

    # Demo queries
    demo_queries = [
        "What's the weather like in Tokyo?",
        "Calculate 5 * 3",
        "Find me news about machine learning",
        "Hello! How are you doing today?"
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


if __name__ == '__main__':
    run_demo()
