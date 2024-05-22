import logger_utils
import hashlib
from models.base import DataModel, VectorDBDataModel
from models.raw import ArticleRawModel
from models.clean import ArticleCleanedModel
from models.chunk import ArticleChunkModel
from models.embedded_chunk import ArticleEmbeddedChunkModel
from utils.cleaning import clean_text
from utils.chunking import chunk_text
from utils.embeddings import embedd_text

logger = logger_utils.get_logger(__name__)

class RawDataHandler:
    @staticmethod
    def handle_mq_message(message: dict) -> DataModel:
        data_type = message.get("type")

        logger.info("Received message.", data_type=data_type)
        if data_type == "articles":
            return ArticleRawModel(**message)
        else:
            raise ValueError("Unsupported data type")

class CleaningHandler:

    @staticmethod
    def handle_raw_message(raw_message: DataModel) -> VectorDBDataModel:
        if isinstance(raw_message, ArticleRawModel):
            try:
                return ArticleCleanedModel(
                    entry_id=raw_message.entry_id,
                    source=raw_message.source,
                    title=raw_message.title,
                    cleaned_content=clean_text("".join(raw_message.content)),
                    summary=raw_message.summary,
                    type="article",
                )
            except Exception as e:
                print(e)
                return {"failed": raw_message}
        else:
            raise ValueError("Unsupported data type")

class ChunkingHandler:
    @staticmethod
    def handle_message(clean_message: VectorDBDataModel):
        if isinstance(clean_message, ArticleCleanedModel):
            data_models_list = []

            text_content = clean_message.cleaned_content
            chunks = chunk_text(text_content)

            for chunk in chunks:
                try:
                    model = ArticleChunkModel(
                        entry_id=clean_message.entry_id,
                        title=clean_message.title,
                        chunk_id=hashlib.md5(chunk.encode()).hexdigest(),
                        chunk_content=chunk,
                        type=clean_message.type,
                    )
                except Exception as e:
                    print(e.errors())
                    raise e
                
                data_models_list.append(model)

            return data_models_list
        else:
            raise ValueError("Unsupported data type")

class EmbeddingHandler:
    @staticmethod
    def handle_message(chunk_model: VectorDBDataModel) -> VectorDBDataModel:
        if isinstance(chunk_model, ArticleChunkModel):
            return ArticleEmbeddedChunkModel(
                entry_id=chunk_model.entry_id,
                title=chunk_model.title,
                chunk_content=chunk_model.chunk_content,
                chunk_id=chunk_model.chunk_id,
                embedded_content=embedd_text(chunk_model.chunk_content),
                type=chunk_model.type,
            )
        else:
            raise ValueError("Unsupported data type")
