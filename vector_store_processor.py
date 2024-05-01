# vector_store_processor.py
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


# Class for handling document loading and processing
class DocumentProcessor:
    def __init__(self, text_path):
        self.text_path = text_path
        self.loaders = {
            '.txt': DirectoryLoader(self.text_path, loader_cls=TextLoader),
        }

    def load_documents(self):
        docs = []
        for loader in self.loaders.values():
            docs.extend(loader.load())
        return docs

    @staticmethod
    def pretty_print_docs(docs):
        output = (f"\n{'-' * 100}\n".join([f"Document {i + 1}:\n\n{d.page_content}" for i, d in enumerate(docs)]))
        return output

    def get_formatted_docs_callable(self):
        """
        Returns a callable that accepts an argument and returns the formatted documents.
        """
        def formatted_docs(_unused_input):
            docs = self.load_documents()
            return self.pretty_print_docs(docs)

        return formatted_docs


# Class for embedding and vector storage
class VectorStorage:
    def __init__(self, documents, persist_directory):
        self.embedding = embeddings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150
        )
        self.splits = self.text_splitter.split_documents(documents)
        self.vectordb = Chroma.from_documents(
            documents=self.splits,
            embedding=self.embedding,
            persist_directory=persist_directory
        )

    def get_retriever(self):
        return self.vectordb.as_retriever()
