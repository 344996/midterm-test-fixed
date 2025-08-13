try:
    from langchain.tools import BaseTool
except Exception:
    class BaseTool:
        pass

"""LangChain router implementation for handling different query types."""

from typing import List, Optional

class QueryRouter:
    def __init__(self, llm: Optional[object], tools: List[BaseTool]):
        self.llm = llm
        self.tools = tools or []
        self.tool_map = {tool.name: tool for tool in self.tools}

    def route_query(self, query: str) -> str:
        q = query.lower()
        if "weather" in q or "temperature" in q:
            return "weather_search" if "weather_search" in self.tool_map else "general_chat"
        if "calculate" in q or any(op in q for op in ['+', '-', '*', '/']) or "what is" in q:
            return "calculator" if "calculator" in self.tool_map else "general_chat"
        if "news" in q or "headline" in q or ("find" in q and "news" in q):
            return "news_search" if "news_search" in self.tool_map else "general_chat"
        return "general_chat"

    def execute_tool(self, tool_name: str, query: str) -> str:
        if tool_name not in self.tool_map:
            return "I'm not sure how to help with that. Could you please rephrase your question?"
        tool = self.tool_map[tool_name]
        q = query.lower()
        if tool_name == "weather_search":
            if " in " in q:
                param = query.split(" in ",1)[1].strip().rstrip("? .")
            else:
                param = q.split()[-1].strip().rstrip("? .")
        elif tool_name == "calculator":
            import re
            m = re.search(r"(\d+\s*[\+\-\*/]\s*\d+)", q)
            param = m.group(1) if m else query
        elif tool_name == "news_search":
            if "about" in q:
                param = query.split("about",1)[1].strip().rstrip("? .")
            else:
                param = query
        else:
            param = query
        try:
            return tool._run(param)
        except Exception as e:
            return f"Error executing tool: {str(e)}"

class ConversationRouter:
    def __init__(self, llm: Optional[object], tools: List[BaseTool]):
        self.llm = llm
        self.query_router = QueryRouter(llm, tools)
        self.conversation_history = []

    def process_message(self, message: str) -> str:
        self.conversation_history.append({"role":"user","content":message})
        tool_name = self.query_router.route_query(message)
        if tool_name == "general_chat":
            if not self.llm:
                return "I'm a mock assistant (no LLM). I can answer simple questions or use tools."
            return "(LLM response placeholder)"
        else:
            response = self.query_router.execute_tool(tool_name, message)
            self.conversation_history.append({"role":"assistant","content":response})
            return response
