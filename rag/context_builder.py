from rag.retriever import retrieve_schema


def build_schema_context(query, top_k=3):
    results = retrieve_schema(query, top_k)

    tables = []
    relationships = []

    for result in results:
        document = result

        metadata = document["metadata"]

        if metadata["type"] == "table":
            tables.append(document["text"])

        elif metadata["type"] == "relationship":
            relationships.append(document["text"])

    context_parts = []

    context_parts.append("RELEVANT DATABASE SCHEMA\n")

    if tables:
        context_parts.append("TABLES:\n")

        for table in tables:
            context_parts.append(table)
            context_parts.append("\n")

    if relationships:
        context_parts.append("RELATIONSHIPS:\n")

        for relationship in relationships:
            context_parts.append(relationship)
            context_parts.append("\n")

    return "\n".join(context_parts)


