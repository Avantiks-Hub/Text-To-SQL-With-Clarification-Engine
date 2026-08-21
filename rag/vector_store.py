import faiss
import numpy as np

from rag.embeddings import create_embeddings


def create_vector_store():

    documents, embeddings = create_embeddings()

    embeddings = np.asarray(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index, documents


