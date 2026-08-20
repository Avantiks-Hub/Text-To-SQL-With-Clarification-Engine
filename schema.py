from sqlalchemy import create_engine,inspect
import json

engine=create_engine( "postgresql+psycopg2://postgres:2806@localhost:5432/learning_db")

inspector=inspect(engine)
tables=inspector.get_table_names()

schema={}
relationships=[]
for table in tables:
    schema[table]={
        "columns":{},
        "primary_key":[],
        "foreign_keys":[]
    }
    cols=inspector.get_columns(table)
    for col in cols:
        schema[table]["columns"][col["name"]]=str(col["type"])
    
    pk=inspector.get_pk_constraint(table)
    schema[table]["primary_key"]=(pk.get('constrained_columns',[]))

    fks=inspector.get_foreign_keys(table)
    for fk in fks:
        cons_col=fk["constrained_columns"]
        ref_col=fk["referred_columns"]
        for column,ref_column in zip(cons_col,ref_col):
            schema[table]["foreign_keys"].append({
                "column":column,
                "references":(
                f"{fk['referred_table']}.{ref_column}"
            )
            })
# print(json.dumps(schema,indent=2))
for table, table_info in schema.items():

    for fk in table_info["foreign_keys"]:

        relationships.append({
            "from_table": table,
            "from_column": fk["column"],
            "to_table": fk["references"].split(".")[0],
            "to_column": fk["references"].split(".")[1]
        })

graph={
    table:[]
    for table in schema
}
# print(schema.items())
for table, table_info in schema.items():
    for fk in table_info["foreign_keys"]:
        referenced_table = fk["references"].split(".")[0]
        graph[table].append(referenced_table)
        graph[referenced_table].append(table)

