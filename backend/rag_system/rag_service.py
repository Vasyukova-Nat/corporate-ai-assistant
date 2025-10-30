from typing import Dict
import ollama
from .simple_ingest_component import SimpleIngestComponent

class RAGService:
    def __init__(self, data_dir: str = "./data"):
        self.ingest_component = SimpleIngestComponent(persist_dir=data_dir)
        # self.model = "llama3.1:8b"
        # self.model = "llama3.2:1b"
        self.model = "qwen2.5:0.5b"
    
    def add_document(self, file_path: str) -> Dict:
        """Добавить документ в базу знаний"""
        try:
            success = self.ingest_component.ingest_file(file_path)
            return {
                "success": success,
                "file_path": file_path,
                "message": "Document successfully added to knowledge base" if success else "Failed to add document"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def query_documents(self, question: str) -> Dict:
        """Поиск по документам с генерацией ответа"""
        try:
            relevant_docs = self.ingest_component.query(question)
            
            context = "\n\n".join([doc.text for doc in relevant_docs[:3]])  # Берем топ-3
            
            if context:
                prompt = f"""
                Ты корпоративный AI-ассистент. Используй предоставленную информацию из базы знаний компании для ответа на вопрос.

                КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ КОМПАНИИ:
                {context}

                ВОПРОС ПОЛЬЗОВАТЕЛЯ:
                {question}

                ОТВЕТ (будь точным и используй только информацию из контекста):
                """
            else:
                prompt = f"""
                Ты корпоративный AI-ассистент. Ответь на вопрос на основе твоих общих знаний о бизнес-процессах.

                ВОПРОС: {question}

                ОТВЕТ:
                """
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={'temperature': 0.3}
            )
            
            return {
                "answer": response['response'],
                "sources_used": len(relevant_docs),
                "sources_preview": [doc.metadata.get('file_name', 'Unknown') for doc in relevant_docs[:3]],
                "context_length": len(context)
            }
            
        except Exception as e:
            return {"error": str(e), "answer": "Извините, произошла ошибка при поиске в документах"}
    
    def get_knowledge_base_stats(self) -> Dict:
        """Получить статистику базы знаний"""
        return self.ingest_component.get_stats()