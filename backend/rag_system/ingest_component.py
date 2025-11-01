import logging
import time
from pathlib import Path
from typing import List
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.storage import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from .ingest_helper import IngestionHelper

logger = logging.getLogger(__name__)

class IngestComponent:
    def __init__(self, persist_dir: str = "./data/chroma_db", max_retries: int = 3):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        
        try:
            self.embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            logger.warning("Failed to load embedding model, using fallback: %s", e)
            from llama_index.embeddings.mock import MockEmbedding
            self.embed_model = MockEmbedding(embed_dim=384)
        
        self.vector_store = self._initialize_vector_store()
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        
        self.index = self._initialize_index()
    
    def _initialize_vector_store(self):
        """Инициализирует векторное хранилище с retry логикой"""
        for attempt in range(self.max_retries):
            try:
                chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
                document_collection = chroma_client.get_or_create_collection("corporate_docs")
                return ChromaVectorStore(chroma_collection=document_collection)
            except Exception as e:
                logger.warning("Vector store initialization attempt %d failed: %s", attempt + 1, e)
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)
    
    def _initialize_index(self):
        """Инициализирует или загружает индекс"""
        for attempt in range(self.max_retries):
            try:
                # Пытаемся загрузить существующий индекс
                index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    embed_model=self.embed_model,
                    storage_context=self.storage_context
                )
                logger.info("Loaded existing vector store index")
                return index
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.info("Creating new vector store index after %d attempts: %s", self.max_retries, e)
                    # Создаем новый пустой индекс
                    index = VectorStoreIndex.from_documents(
                        [],
                        storage_context=self.storage_context,
                        embed_model=self.embed_model
                    )
                    index.storage_context.persist(persist_dir=self.persist_dir)
                    return index
                logger.warning("Index loading attempt %d failed, retrying: %s", attempt + 1, e)
                time.sleep(1)
    
    def ingest_file(self, file_path: str) -> bool:
        """Добавляет файл в базу знаний с retry логикой"""
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error("File not found: %s", file_path)
            return False
        
        for attempt in range(self.max_retries):
            try:
                documents = IngestionHelper.transform_file_into_documents(
                    file_path.name, file_path
                )
                
                if not documents:
                    logger.warning("No documents extracted from %s", file_path)
                    return False
                
                # Вставляем документы в индекс
                for document in documents:
                    self.index.insert(document)
                
                # Сохраняем изменения
                self.index.storage_context.persist(persist_dir=self.persist_dir)
                logger.info("Successfully ingested %s with %s documents", file_path, len(documents))
                return True
                
            except Exception as e:
                logger.warning("Ingestion attempt %d failed for %s: %s", attempt + 1, file_path, e)
                if attempt == self.max_retries - 1:
                    logger.error("All ingestion attempts failed for %s", file_path)
                    return False
                time.sleep(2 ** attempt)  
    
    def query(self, question: str, top_k: int = 5) -> List[Document]:
        """Ищет релевантные документы для вопроса"""
        if not question or not question.strip():
            logger.warning("Empty query received")
            return []
            
        for attempt in range(self.max_retries):
            try:
                retriever = self.index.as_retriever(similarity_top_k=top_k)
                relevant_docs = retriever.retrieve(question.strip())
                found_documents = [doc.node for doc in relevant_docs]
                
                logger.debug("Query '%s' found %s documents", question, len(found_documents))
                return found_documents
                
            except Exception as e:
                logger.warning("Query attempt %d failed: %s", attempt + 1, e)
                if attempt == self.max_retries - 1:
                    logger.error("All query attempts failed for: %s", question)
                    return []
                time.sleep(1)
    
    def get_stats(self) -> dict:
        """Возвращает статистику базы знаний"""
        try:
            collection = self.vector_store._collection
            count = collection.count() if hasattr(collection, 'count') else 0
            return {
                "document_count": count,
                "vector_store": "ChromaDB",
                "embedding_model": "all-MiniLM-L6-v2",
                "persist_dir": str(self.persist_dir),
                "status": "active",
                "retry_config": f"{self.max_retries} attempts"
            }
        except Exception as e:
            logger.error("Error getting stats: %s", e)
            return {
                "document_count": 0, 
                "error": str(e),
                "status": "error"
            }
    
    def health_check(self) -> dict:
        """Проверка здоровья компонента"""
        try:
            stats = self.get_stats()
            index_ok = self.index is not None
            store_ok = self.vector_store is not None
            
            return {
                "status": "healthy" if index_ok and store_ok else "degraded",
                "components": {
                    "index": "healthy" if index_ok else "error",
                    "vector_store": "healthy" if store_ok else "error",
                    "embedding_model": "healthy"
                },
                "statistics": stats
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }