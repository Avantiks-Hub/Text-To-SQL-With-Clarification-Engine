import hashlib
import json
from pathlib import Path

import faiss
import numpy as np

from rag.documents import create_schema_doc
from rag.embeddings import create_embeddings


INDEX_DIR = Path(__file__).parent / "index"

INDEX_FILE = INDEX_DIR / "schema.index"
DOCUMENTS_FILE = INDEX_DIR / "documents.json"
METADATA_FILE = INDEX_DIR / "metadata.json"


def calculate_schema_hash(documents):
    """
    Create a fingerprint of the schema documents.

    If the schema documents change, the hash will change.
    """

    serialized = json.dumps(
        documents,
        sort_keys=True
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def build_vector_store():

    print("Building schema vector store...")

    documents, embeddings = create_embeddings()

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    INDEX_DIR.mkdir(exist_ok=True)

    faiss.write_index(
        index,
        str(INDEX_FILE)
    )

    with open(DOCUMENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            documents,
            file,
            indent=2
        )

    schema_hash = calculate_schema_hash(documents)

    metadata = {
        "schema_hash": schema_hash,
        "vector_dimension": dimension,
        "number_of_documents": len(documents)
    }

    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            indent=2
        )

    print("Vector store built successfully.")

    return index, documents


def load_vector_store():

    index = faiss.read_index(
        str(INDEX_FILE)
    )

    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    return index, documents


def is_index_up_to_date():

    if not (
        INDEX_FILE.exists()
        and DOCUMENTS_FILE.exists()
        and METADATA_FILE.exists()
    ):
        return False

    current_documents = create_schema_doc()

    current_hash = calculate_schema_hash(
        current_documents
    )

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return current_hash == metadata["schema_hash"]


def get_vector_store():

    if is_index_up_to_date():

        return load_vector_store()

    return build_vector_store()


