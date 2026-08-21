import numpy as np

from rag.embeddings import SentenceTransformer, MODEL_NAME
from rag.vector_store import create_vector_store
from schema import graph

def retrieve_schema(query, top_k=3):
    
    # Create/load the embedding model
    model = SentenceTransformer(MODEL_NAME)

    # Create FAISS index and get original documents
    index, documents = create_vector_store()

    # Convert the user query into an embedding
    query_embedding = model.encode([query])

    query_embedding = np.asarray(query_embedding).astype("float32")

    # Search FAISS
    distances, indices = index.search(query_embedding, top_k)

    initial_tables = set()

    for index_position in indices[0]:

        document = documents[index_position]

        metadata = document["metadata"]

        if metadata["type"] == "table":
            initial_tables.add(metadata["table"])

        elif metadata["type"] == "relationship":
            initial_tables.add(metadata["from_table"])
            initial_tables.add(metadata["to_table"])

    expanded_tables = expand_with_graph(initial_tables)

    results = []

    for document in documents:

        metadata = document["metadata"]

        if metadata["type"] == "table":
            if metadata["table"] in expanded_tables:
                results.append(document)

        elif metadata["type"] == "relationship":
            if (
                metadata["from_table"] in expanded_tables
                and metadata["to_table"] in expanded_tables
            ):
                results.append(document)

    return results

def expand_with_graph(tables):
    expanded_tables = set(tables)

    for table in tables:
        neighbors = graph.get(table, [])

        for neighbor in neighbors:
            expanded_tables.add(neighbor)

    return list(expanded_tables)


if __name__ == "__main__":

    query = "Which students are enrolled in Machine Learning?"

    results = retrieve_schema(query)

    for result in results:
        print("=" * 60)
        print(result["text"])
        print(result["metadata"])