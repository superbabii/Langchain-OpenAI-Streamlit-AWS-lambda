# custom_tools_agent.py

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from typing import Type, Optional, Union


# Tool for retrieving messages
class ToolAskUserToValidateBDDInput(BaseModel):
    ask_question: str = Field(description="The BDD statement to validate")


# Custom tool class for retrieving messages
class CustomValidationTool(BaseTool):
    name: str = "custom_validation_tool"
    description: str = "Tool that asks a user to validate a BDD statement."
    args_schema: Type[BaseModel] = ToolAskUserToValidateBDDInput  # Specify your input schema here

    def _run(
        self,
        ask_question: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, None]:
        try:
            user_response = self.validate_function(ask_question)
            return user_response
        except Exception as e:
            return repr(e)

    def validate_function(self, input_data):
        """Ask user to validate BDD statement."""
        try:
            print("Validate function input:", input_data)
            user_input = "User validated input"  # Placeholder for actual user input
            return user_input
        except Exception as e:
            return f"An error occurred: {e}"
