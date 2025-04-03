# vector_db/client.py
import os
from pinecone import Pinecone

class PineconeConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "default-index")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "default")
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self.pc.Index(self.index_name)

    def get_index(self):
        """Returns the Pinecone index instance"""
        return self.index

    def get_namespace(self):
        """Returns the active namespace"""
        return self.namespace

# Singleton instance
pinecone = PineconeConnection()