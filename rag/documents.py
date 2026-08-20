from schema import schema,relationships

def create_schema_doc():
    doc=[]

    # create documents for tables
    for table_name,table_info in schema.items():
        cols=[]

        for column_name,column_type in table_info["columns"].items():
            cols.append(f"{column_name}:{column_type}")

        text=f'''
Table:{table_name}

Columns:
{chr(10).join(cols)}

Primary Keys:
{", ".join(table_info["primary_key"])}
'''.strip()

        doc.append({
            "text":text,
            "metadata":{
                "type":"table",
                "table":table_name
            }
        })

    # create documents for realtionships
    for relationship in relationships:
        text=f'''
Relationship:
{relationship["from_table"]}.{relationship["from_column"]}
references
{relationship["to_table"]}.{relationship["to_column"]}
'''.strip()
        doc.append({
            "text":text,
            "metadata":{
                "type":"relationship",
                "from_table":relationship["from_table"],
                "to_table":relationship["to_table"]
            }
        })
    return doc

if __name__ == "__main__":

    documents = create_schema_doc()

    for document in documents:
        print("=" * 60)
        print(document["text"])
        print(document["metadata"])