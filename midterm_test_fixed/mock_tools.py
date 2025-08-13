"""Mock tools for the LangChain application."""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import random

class WeatherSearchInput(BaseModel):
    """Input for weather search tool."""
    location: str = Field(description="The location to get weather for")


class FakeWeatherSearchTool(BaseTool):
    """A mock weather search tool that returns fake weather data."""
    name: str = "weather_search"
    description: str = "Get current weather information for a specific location"
    args_schema: type = WeatherSearchInput

    def _run(self, location: str) -> str:
        conditions = ["sunny", "cloudy", "rainy", "snowy", "partly cloudy", "stormy"]
        temperatures = list(range(-10, 40))  # Celsius
        condition = random.choice(conditions)
        temperature = random.choice(temperatures)
        humidity = random.randint(30, 90)
        wind_speed = random.randint(0, 25)

        return f"""Weather in {location}:
- Condition: {condition}
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Wind Speed: {wind_speed} km/h"""


class CalculatorInput(BaseModel):
    """Input for calculator tool."""
    expression: str = Field(description="Mathematical expression to evaluate")


class FakeCalculatorTool(BaseTool):
    """A mock calculator tool for basic math operations."""
    name: str = "calculator"
    description: str = "Perform basic mathematical calculations"
    args_schema: type = CalculatorInput

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)  # remove +1 bug
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"


class NewsSearchInput(BaseModel):
    """Input for news search tool."""
    topic: str = Field(description="The topic to search news for")


class FakeNewsSearchTool(BaseTool):
    """A mock news search tool that returns fake news headlines."""
    name: str = "news_search"
    description: str = "Search for recent news articles on a specific topic"
    args_schema: type = NewsSearchInput

    def _run(self, topic: str) -> str:
        headlines = [
            f"Breaking: Major developments in {topic} industry",
            f"Experts discuss the future of {topic}",
            f"New research reveals insights about {topic}",
            f"Local community responds to {topic} changes",
            f"Global impact of {topic} continues to grow",
        ]
        selected = random.sample(headlines, k=min(5, len(headlines)))
        return "Recent news about {t}:
{body}".format(
            t=topic, body="\n".join("• " + h for h in selected)
        )
