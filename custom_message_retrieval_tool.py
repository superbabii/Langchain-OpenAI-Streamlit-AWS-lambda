# custom_tools_agent.py

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import List, Type, Optional, Union

from chat_history_sql_db import ChatHistoryDB


# Tool for retrieving messages
class ToolRetrieveMessagesInput(BaseModel):
    query: str = Field(description="Search query for message retrieval")
    max_results: int = Field(default=5, description="Maximum number of messages to retrieve")


# Custom tool class for retrieving messages
class CustomMessageRetrievalTool(BaseTool):
    name: str = "custom_message_retrieval_tool"
    description: str = "Tool that retrieves relevant messages based on user query."
    args_schema: Type[BaseModel] = ToolRetrieveMessagesInput  # Specify your input schema here

    def _run(
        self,
        query: str,
        max_results: int,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[List[str], str]:
        """Use the tool."""
        try:
            chat_db = ChatHistoryDB('chat.db')
            chat_db.initialize()
            relevant_messages = chat_db.retrieve_relevant_messages(query, max_results)
            return relevant_messages
        except Exception as e:
            error_message = f"An error occurred: {repr(e)}"
            return error_message