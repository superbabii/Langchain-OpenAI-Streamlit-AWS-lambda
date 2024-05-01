import os
import tempfile
import json
import boto3
import base64

from langchain import hub
from langchain.agents import AgentExecutor, ConversationalChatAgent
from langchain.retrievers import SelfQueryRetriever
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.llms.bedrock import Bedrock
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders.parsers.pdf import PyPDFParser
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_core.documents import Document

# Load multiple files
from langchain_community.document_loaders import DirectoryLoader, PyPDFDirectoryLoader, TextLoader, \
    CSVLoader
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import Tool

from llm_anthropic_claude import anthropic_claude_llm
from vector_store_processor import VectorStorage
from vector_store_processor import DocumentProcessor

from langchain_community.document_loaders import S3FileLoader

# Initialize Boto3 client for Lambda
lambda_client = boto3.client('lambda')

def split_feature_text_into_scenarios(feature_text, include_comments=False, source="local"):
    scenarios = []
    current_scenario_content = ""
    feature_declared = False
    in_scenario_block = False
    current_tag = ""

    for line in feature_text.split('\n'):
        stripped_line = line.strip()

        if stripped_line.startswith("#") and not include_comments:
            continue

        if stripped_line.startswith("Feature:") and not feature_declared:
            feature_name = stripped_line[len("Feature:"):].strip()
            feature_declared = True
            continue

        if stripped_line.startswith("@"):
            if in_scenario_block:
                # Add the current scenario content to scenarios
                scenarios.append(Document(page_content=current_scenario_content.strip(), metadata=current_metadata))
                current_scenario_content = ""
            current_tag = stripped_line  # Capture the tag
            current_metadata = {"Feature": feature_name, "Tag": current_tag, "source": source}
            current_scenario_content += current_tag + "\n"  # Add the tag at the beginning of scenario content
            in_scenario_block = True
            continue

        if in_scenario_block or stripped_line:
            current_scenario_content += line + "\n"

        if stripped_line.startswith("Scenario:") or stripped_line.startswith("Scenario Outline:"):
            current_metadata["Scenario"] = stripped_line.split(":", 1)[1].strip()
        elif stripped_line.startswith("Description:"):
            current_metadata["Description"] = stripped_line[len("Description:"):].strip()
        elif stripped_line.startswith("Examples:"):
            in_scenario_block = False  # Stop including lines after examples

    # Append the last scenario if it exists
    if current_scenario_content:
        scenarios.append(Document(page_content=current_scenario_content.strip(), metadata=current_metadata))

    return scenarios

class Document:
    def __init__(self, s3_path, page_content, metadata):
        self.s3_path = s3_path
        self.page_content = page_content
        self.metadata = metadata

class LLMRagQA:
    def __int__(self):
        pass

    def load_agent(self, chat_history=None, uploaded_files=None, bucket_name=None):
        if uploaded_files is not None:
            # loaders = {}
            docs = []
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                
                s3_path = f"s3://{bucket_name}/{file_name}"
                # Invoke Lambda function
                response = lambda_client.invoke(
                    FunctionName='load-pdf-from-s3',
                    InvocationType='RequestResponse',
                    Payload=json.dumps({
                        'name': file_name,
                        'bucket': bucket_name
                    })
                )
                
                result = json.loads(response['Payload'].read())
                if isinstance(result, dict) and 'content' in result and 'meta' in result:
                    # Create a Document instance and append it to the list
                    doc_entry = Document(s3_path, result['content'], result['meta'])
                    docs.append(doc_entry)
                else:
                    # Handle the case where the result is not as expected
                    print(f"Invalid result format for file {file_name}: {result}")
                
        # for loader in loaders.values():
        #     print("loader: ", loader)
        #     docs.extend(loader.load())
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=2)
        all_splits = text_splitter.split_documents(docs)
        # Embed the documents and store them in ChromaDB
        # FAISS is a vector store, Self query retriever with Vector Store type FAISS not supported.
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings,
                                            persist_directory="vectorstore")
        vectorstore.persist()

        system_msg = "You are a helpful agent."

        # Time to initialize the LLM, as late as possible so everything not requiring the LLM instance to fail fast
        # Initialize the Bedrock LLM
        llm = anthropic_claude_llm

        # Define a custom template
        template = """
AI Query Refinement Tool for Feature Statement Creation

This tool is designed to refine user queries into detailed and specific requests for creating 
Feature statements. It focuses on understanding and incorporating the context provided by the 
user, ensuring that the refined query is aligned with the requirements for feature scenario and 
feature file creation, as well as validation.

"Refine the query to provide sample feature statements.

---------------------------------------------------------------------------------------------------
Please dont include the context to the response, make response short and informative.
---------------------------------------------------------------------------------------------------
Context:
<ctx> {context} </ctx>
---------------------------------------------------------------------------------------------------

{question} Answer: """

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template,
        )
        # Create a RAG application to get the data from JSON and convert it to BDD statements
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=vectorstore.as_retriever(),
            verbose=True,
            chain_type_kwargs={
                "verbose": True,
                "prompt": prompt,
                "memory": ConversationBufferMemory(
                    memory_key="history",
                    input_key="question",
                    return_messages=True),
            }
        )
        return qa_chain

    def contextualized_question(self, input_prompt: dict):
        """
        First we’ll need to define a sub-chain that takes historical messages and the latest
        user question, and reformulates the question if it makes reference to any information in the
        historical information.
        We’ll use a prompt that includes a MessagesPlaceholder variable under the name “chat_history”.
        This allows us to pass in a list of Messages to the prompt using the “chat_history” input key,
        and these messages will be inserted after the system message and before the human message
        containing the latest question.

        :param input_prompt:
        :return:
        """
        llm = anthropic_claude_llm
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

        if input_prompt.get("chat_history"):
            return contextualize_q_chain
        else:
            return input_prompt["question"]

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def chat_rag_history_langchain(self, question, chat_history):
        llm = anthropic_claude_llm
        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\

        {context}"""
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}")
            ]
        )
        docs_processor = DocumentProcessor(text_path="docs/guide/text_feature")
        docs = docs_processor.load_documents()
        format_docs = docs_processor.get_formatted_docs_callable()
        vector_retriever = VectorStorage(docs, persist_directory="vectorstore")
        retriever = vector_retriever.get_retriever()

        file_path = "docs/guide/text_feature/Acoustics_Gen2.feature"
        with open(file_path, 'r', encoding='utf-8') as file:
            feature_text = file.read()
        # Create Document objects from the scenarios
        documents = split_feature_text_into_scenarios(feature_text, include_comments=True,
                                                      source="local")

        # Embed the documents and store them in ChromaDB
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        # vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings,
        #                                     persist_directory="vectorstore")
        # retriever = vectorstore.persist()
        vector_retriever = VectorStorage(documents, persist_directory="vectorstore")
        retriever = vector_retriever.get_retriever()

        print("qa_prompt: ", qa_prompt)
        rag_chain = (
                RunnablePassthrough.assign(
                    context=self.contextualized_question | retriever
                )
                | qa_prompt
                | llm
        )
        # prompt = hub.pull("rlm/rag-prompt")
        # rag_chain = (
        #         {"context": retriever, "question": RunnablePassthrough()}
        #         | prompt
        #         | llm
        #         | StrOutputParser()
        # )

        # print("rag_chain: ", rag_chain)
        # output = rag_chain.invoke(question)
        output = rag_chain.invoke({"question": question, "chat_history": chat_history})
        # print("output: ", output)
        # AIMessage
        return output

