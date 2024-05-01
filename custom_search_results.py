# custom_tools_agent.py

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.vectorstores.faiss import FAISS
from pydantic import Field, BaseModel
from typing import List, Type, Optional, Union, Dict, Any

from app_constants import get_scenario_path
from vector_store_processor import DocumentProcessor, embeddings
from streamlit_sidebar import get_project_name


# Tool for retrieving messages
class ToolSearchInput(BaseModel):
    query: str = Field(description="The search query")


# Custom tool class for retrieving messages
class CustomSearchResults(BaseTool):
    name: str = "custom_search_results"
    description: str = "Tool that searches for documents and returns relevant results."
    args_schema: Type[BaseModel] = ToolSearchInput

    def _run(
            self,
            query: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[List[Dict], str]:
        """Use the tool."""
        try:
            get_project_name_from_sidebar = get_project_name()
            print("Loading documents get_project_name:", get_project_name_from_sidebar)
            if get_project_name_from_sidebar:
                scenario_path = get_scenario_path(get_project_name_from_sidebar)
            else:
                return "Error, user did not select a project type."
            print("Loading documents from:", scenario_path)
            documents = TextLoader(scenario_path).load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            splits = text_splitter.split_documents(documents)
            print(f"Split {len(splits)} documents")
            retriever = FAISS.from_documents(splits, embeddings).as_retriever()
            output = retriever.get_relevant_documents(query)
            return DocumentProcessor.pretty_print_docs(output)
        except Exception as e:
            print("Error retrieving documents:", e)
            return repr(e)