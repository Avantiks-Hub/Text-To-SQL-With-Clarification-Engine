import os 
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel,Field
from rag.context_builder import build_schema_context

load_dotenv()

class Filter(BaseModel):
    column: str
    operator: str
    value: str


class Aggregation(BaseModel):
    function: str
    column: str


class OrderBy(BaseModel):
    column: str
    direction: str


class QueryAnalysis(BaseModel):

    # What does the user want?
    intent_type: str
    intent_description: str

    # Database objects
    tables: list[str]

    # SELECT columns
    selected_columns: list[str]

    # WHERE conditions
    filters: list[Filter]

    # COUNT / SUM / AVG / MIN / MAX
    aggregations: list[Aggregation]

    # GROUP BY
    group_by: list[str]

    # ORDER BY
    order_by: list[OrderBy]

    # LIMIT
    limit: int | None

    # Human concepts mentioned by the user
    entities: list[str]

    # Clarification information
    is_ambiguous: bool
    ambiguity_reason: str
    missing_information: list[str]

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_query(user_ques:str) -> QueryAnalysis:
    schema_context=build_schema_context(
        user_ques,
        top_k=3
    )

    prompt = f"""
You are the Query Analyzer for a Text-to-SQL system.

Your job is to understand what the user wants from the database.

DO NOT generate SQL.

Use ONLY the database schema provided below.

DATABASE SCHEMA:
{schema_context}

USER QUESTION:
{user_ques}

Analyze the question and return structured information.

Determine:

1. intent_type
   Use one of these values when applicable:
   - SELECT
   - COUNT
   - SUM
   - AVG
   - MIN
   - MAX
   - GROUP_BY
   - ORDER_BY

2. intent_description
   Briefly describe what the user wants.

3. entities
   Important concepts or values mentioned by the user.

4. tables
   Database tables required to answer the request.

5. filters
   Explicit conditions stated by the user.
   
   For each filter provide:
   - column: the fully qualified database column if known
   - value: the value specified by the user

   Do NOT invent filters.

6. is_ambiguous
   Set to true when the request does not contain enough information
   to determine the intended query reliably.

7. ambiguity_reason
   Explain why the request is ambiguous.

8. missing_information
   List the specific information that is missing.

IMPORTANT:

A request such as:
"Show me students"
or
"Show me all courses"

is NOT ambiguous if the user clearly identifies the table or entity
and a reasonable SELECT * interpretation is possible.

Do not mark a query ambiguous merely because a requested
column or table does not exist.

Represent the user's requested query plan first.

Schema validity will be checked separately by the Schema Validator.

Only set is_ambiguous=true when information is genuinely missing
from the user's request and cannot be reasonably inferred.

Examples of genuinely ambiguous requests:

"Show me the top students."
→ Missing ranking criterion.

"Show me students from the department."
→ Missing department.

"Show me courses with high credits."
→ Missing definition of "high".

"Show me the students."
→ If multiple student groups or interpretations exist in the
provided context, clarification may be required.

A request such as:
"Which students are enrolled in Machine Learning?"

is sufficiently specific because the requested entity,
relationship, and filtering condition can be determined.

Do not invent information that the user did not provide.

Return a structured query plan.

selected_columns:
Columns that should appear in the SELECT result.

Use fully qualified names when known:
students.name
courses.course_name

If the user asks for all columns, use:
["*"]

filters:
Represent every filtering condition explicitly stated by the user.

For each filter provide:
- column
- operator
- value

Supported operators:
=, !=, >, <, >=, <=, LIKE

If the user explicitly refers to an attribute or column that does
not exist in the schema, still represent the user's requested
column reference in the filter using the most appropriate table
based on the user's request.

Do NOT silently remove a requested filter just because the column
does not exist.

The Schema Validator will determine whether the referenced
column actually exists.

Example:

User:
"Show me students with GPA above 8."

If the students table does not contain GPA, still produce:

{{
  "column": "students.gpa",
  "operator": ">",
  "value": "8"
}}

The analyzer must not remove the condition.

aggregations:
Use for COUNT, SUM, AVG, MIN, MAX.

Example:
COUNT(students.student_id)

group_by:
Columns explicitly required for grouping.

order_by:
Columns used to sort the result.

For every order_by item provide:
- column
- direction

direction must be:
ASC
or
DESC

limit:
Use only when the user explicitly requests a number of results,
such as "top 5 students".

If no limit is specified:
null

entities:
Important natural-language concepts mentioned by the user.
Entities are NOT necessarily database columns.

IMPORTANT:
Every database column reference in selected_columns,
filters, aggregations, group_by, and order_by must be grounded
in the provided database schema.

Never invent a column.
"""
    response=client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": QueryAnalysis,
        }
    )

    return QueryAnalysis.model_validate_json(response.text)

if __name__ == "__main__":

    questions = [
        "Show me students with GPA above 8."
    ]

    for question in questions:

        print("\n" + "=" * 80)
        print("QUESTION:", question)
        print("=" * 80)

        result = analyze_query(question)

        print(result.model_dump_json(indent=2))