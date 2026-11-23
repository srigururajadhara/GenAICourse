from app.services.answering import AnsweringService
from app.services.ingestion import IngestionService
from app.services.summarization import SummarizationService

ingestion_service = IngestionService()
answering_service = AnsweringService()
summarization_service = SummarizationService()
