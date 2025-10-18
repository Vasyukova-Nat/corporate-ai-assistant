import logging
from pathlib import Path
from typing import List
from llama_index.core.schema import Document
from llama_index.core import SimpleDirectoryReader

logger = logging.getLogger(__name__)

class SimpleIngestionHelper:
    @staticmethod
    def transform_file_into_documents(file_name: str, file_data: Path) -> List[Document]:
        """Преобразует файл в документы - упрощенная версия"""
        try:
            documents = SimpleIngestionHelper._load_file_to_documents(file_name, file_data)
            for document in documents:
                document.metadata["file_name"] = file_name
            return documents
        except Exception as e:
            logger.error(f"Error processing file {file_name}: {e}")
            return []

    @staticmethod
    def _load_file_to_documents(file_name: str, file_data: Path) -> List[Document]:
        """Загружает файл в документы используя SimpleDirectoryReader"""
        try:
            # SimpleDirectoryReader автоматически определяет тип файла по расширению
            # и использует соответствующий ридер
            reader = SimpleDirectoryReader()
            
            if isinstance(file_data, Path) and file_data.exists():
                documents = reader.load_data(file_data)
            else:
                # Если file_data - это содержимое файла, создаем временный файл
                temp_file = Path("temp_file")
                try:
                    if hasattr(file_data, 'read_text'):
                        temp_file.write_text(file_data.read_text(), encoding='utf-8')
                    else:
                        temp_file.write_text(str(file_data), encoding='utf-8')
                    documents = reader.load_data(temp_file)
                finally:
                    if temp_file.exists():
                        temp_file.unlink()  
            
            return documents
            
        except Exception as e:
            logger.error(f"Error loading file {file_name}: {e}")
            # Fallback: пытаемся прочитать как текстовый файл
            try:
                if isinstance(file_data, Path) and file_data.exists():
                    text_content = file_data.read_text(encoding='utf-8', errors='ignore')
                else:
                    text_content = str(file_data)
                
                # Создаем документ вручную
                return [Document(
                    text=text_content,
                    metadata={"file_name": file_name}
                )]
            except Exception as fallback_error:
                logger.error(f"Fallback also failed for {file_name}: {fallback_error}")
                return []