import logging
from pathlib import Path
from typing import List
from llama_index.core.schema import Document
from llama_index.core.readers import StringIterableReader

logger = logging.getLogger(__name__)

class IngestionHelper:
    """Хелпер для обработки файлов"""
    # Набор поддерживаемых форматов
    SUPPORTED_EXTENSIONS = {
        '.txt': StringIterableReader,
        '.md': StringIterableReader,
        '.json': StringIterableReader,
    }
    
    @staticmethod
    def transform_file_into_documents(file_name: str, file_data: Path) -> List[Document]:
        """Преобразует файл в документы"""
        try:
            documents = IngestionHelper._load_file_to_documents(file_name, file_data)
            for document in documents:
                document.metadata["file_name"] = file_name
                document.excluded_embed_metadata_keys = ["file_name"]
                document.excluded_llm_metadata_keys = ["file_name"]
            return documents
        except Exception as e:
            logger.error("Error processing file %s: %s", file_name, e)
            return []

    @staticmethod
    def _load_file_to_documents(file_name: str, file_data: Path) -> List[Document]:
        """Загружает файл в документы"""
        extension = Path(file_name).suffix.lower()
        reader_cls = IngestionHelper.SUPPORTED_EXTENSIONS.get(extension)
        
        if reader_cls is None:
            logger.debug(f"No specific reader for {extension}, using default string reader")
            # Читаем как текстовый файл
            return IngestionHelper._read_as_text(file_data)
        
        logger.debug(f"Using {reader_cls.__name__} for {file_name}")
        try:
            documents = reader_cls().load_data(file_data)
            # Очистка от NUL байтов 
            for doc in documents:
                doc.text = doc.text.replace("\u0000", "")
            return documents
        except Exception:
            return IngestionHelper._read_as_text(file_data)

    @staticmethod
    def _read_as_text(file_data: Path) -> List[Document]:
        """Читает файл как простой текст"""
        try:
            if isinstance(file_data, Path) and file_data.exists():
                text_content = file_data.read_text(encoding='utf-8', errors='ignore')
            else:
                text_content = str(file_data)
            
            reader = StringIterableReader()
            documents = reader.load_data([text_content])
            return documents
        except Exception as e:
            logger.error(f"Fallback text reading also failed: {e}")  
            return []