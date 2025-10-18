import logging
from pathlib import Path
from typing import List
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.storage import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from .simple_ingest_helper import SimpleIngestionHelper
# from .components.ingest.ingest_helper import IngestionHelper

logger = logging.getLogger(__name__)

class SimpleIngestComponent:
    """Упрощенная версия ингест компонента из PrivateGPT"""
    
    def __init__(self, persist_dir: str = "./data/chroma_db"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.vector_store = self._initialize_vector_store()
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        
        self.index = self._initialize_index()
    
    def _initialize_vector_store(self):
        """Инициализирует векторное хранилище"""
        chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
        chroma_collection = chroma_client.get_or_create_collection("corporate_docs")
        return ChromaVectorStore(chroma_collection=chroma_collection)
    
    def _initialize_index(self):
        """Инициализирует или загружает индекс"""
        try:
            index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                embed_model=self.embed_model,
                storage_context=self.storage_context
            )
            logger.info("Loaded existing vector store index")
        except Exception as e:
            logger.info("Creating new vector store index")
            index = VectorStoreIndex.from_documents(
                [],
                storage_context=self.storage_context,
                embed_model=self.embed_model
            )
            index.storage_context.persist(persist_dir=self.persist_dir)
        
        return index
    
    def ingest_file(self, file_path: str) -> bool:
        """Добавляет файл в базу знаний"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            documents = SimpleIngestionHelper.transform_file_into_documents(
                file_path.name, file_path
            )
            
            if not documents:
                logger.warning(f"No documents extracted from {file_path}")
                return False
            
            for document in documents:
                self.index.insert(document)
            
            self.index.storage_context.persist(persist_dir=self.persist_dir)
            logger.info(f"Successfully ingested {file_path} with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
            return False
    
    def query(self, question: str, top_k: int = 5) -> List[Document]:
        """Ищет релевантные документы для вопроса"""
        try:
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            relevant_docs = retriever.retrieve(question)
            return [doc.node for doc in relevant_docs]
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Возвращает статистику базы знаний"""
        try:
            collection = self.vector_store._collection
            count = collection.count() if hasattr(collection, 'count') else 0
            return {
                "document_count": count,
                "vector_store": "ChromaDB",
                "embedding_model": "all-MiniLM-L6-v2"
            }
        except:
            return {"document_count": 0, "error": "Unable to get stats"}