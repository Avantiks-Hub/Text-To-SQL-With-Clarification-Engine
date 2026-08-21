from sentence_transformers import SentenceTransformer
from rag.documents import create_schema_doc


MODEL_NAME = "all-MiniLM-L6-v2"


def create_embeddings():
    documents = create_schema_doc()

    model = SentenceTransformer(MODEL_NAME)

    texts = [document["text"] for document in documents]

    embeddings = model.encode(texts)

    return documents, embeddings
