"""LangChain router implementation for handling different query types."""

from typing import List
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool


class QueryRouter:
    """Routes queries to appropriate tools based on content analysis."""
    def __init__(self, llm: ChatGoogleGenerativeAI, tools: List[BaseTool]):
        self.llm = llm
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}

        # Create routing prompt
        self.routing_prompt = PromptTemplate(
            input_variables=["query", "available_tools"],
            template=(
                "You are a strict router. Available tools (one per line):\n"
                "{available_tools}\n\n"
                "Return ONLY the tool name that best matches the user query from this exact set: "
                "weather_search, calculator, news_search. If none fits, return general_chat.\n\n"
                "Query: {query}\n"
                "Tool name only:"
            ),
        )
        self.routing_chain = self.routing_prompt | self.llm | StrOutputParser()

    def route_query(self, query: str) -> str:
        tool_descriptions = [f"- {tool.name}: {tool.description}" for tool in self.tools]
        available_tools = "\n".join(tool_descriptions)

        result = self.routing_chain.invoke(
            {"query": query, "available_tools": available_tools}
        )
        tool_name = result.strip().lower()
        return tool_name if tool_name in self.tool_map else "general_chat"

    def execute_tool(self, tool_name: str, query: str) -> str:
        if tool_name not in self.tool_map:
            return "I'm not sure how to help with that. Could you please rephrase your question?"

        tool = self.tool_map[tool_name]

        param_extraction_prompt = PromptTemplate(
            input_variables=["query", "tool_description"],
            template=(
                "Extract the SINGLE argument string needed for this tool based on its description.\n"
                "- If weather_search: return only the location.\n"
                "- If calculator: return only the math expression.\n"
                "- If news_search: return only the topic.\n\n"
                "Tool description: {tool_description}\n"
                "User query: {query}\n"
                "Return only the argument string, no quotes, no labels."
            ),
        )
        param_chain = param_extraction_prompt | self.llm | StrOutputParser()
        parameter = param_chain.invoke(
            {"query": query, "tool_description": f"{tool.name}: {tool.description}"}
        ).strip()

        try:
            return tool._run(parameter)
        except Exception as e:
            return f"Error executing tool: {str(e)}"


class ConversationRouter:
    """Advanced router that maintains conversation context."""
    def __init__(self, llm: ChatGoogleGenerativeAI, tools: List[BaseTool]):
        self.llm = llm
        self.query_router = QueryRouter(llm, tools)
        self.conversation_history = []

    def process_message(self, message: str) -> str:
        self.conversation_history.append({"role": "user", "content": message})
        tool_name = self.query_router.route_query(message)
        if tool_name == "general_chat":
            response = self._handle_general_chat(message)
        else:
            response = self.query_router.execute_tool(tool_name, message)
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def _handle_general_chat(self, message: str) -> str:
        context = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-4:]]
        )
        general_prompt = PromptTemplate(
            input_variables=["context", "message"],
            template=(
                "You are a friendly assistant. Use the recent context to reply briefly and helpfully.\n"
                "Context:\n{context}\n\n"
                "User: {message}\n"
                "Assistant:"
            ),
        )
        general_chain = general_prompt | self.llm | StrOutputParser()
        return general_chain.invoke({"context": context, "message": message})
