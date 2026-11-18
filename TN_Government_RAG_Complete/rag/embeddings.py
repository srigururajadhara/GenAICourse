from functools import lru_cache
from fastembed import TextEmbedding

MODEL_NAME = "intfloat/multilingual-e5-large"
EMBEDDING_DIMENSIONS = 1024


@lru_cache(maxsize=1)
def get_model():
    return TextEmbedding(model_name=MODEL_NAME)


def embed_documents(texts):
    if not texts:
        return []
    vectors = get_model().embed([f"passage: {text}" for text in texts])
    return [vector.tolist() for vector in vectors]


def embed_query(question):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    vector = next(get_model().query_embed([f"query: {question}"])).tolist()
    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions; got {len(vector)}"
        )
    return vector
