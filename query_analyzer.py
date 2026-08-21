import os 
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel,Field
from rag.context_builder import build_schema_context

load_dotenv()

class Filter(BaseModel):
    column: str
    value: str


class QueryAnalysis(BaseModel):
    intent_type: str
    intent_description:str

    entities: list[str]
    tables: list[str]
    filters: list[Filter]

    is_ambiguous: bool
    ambiguity_reason: str
    missing_information:list[str]

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

Do not mark a query ambiguous merely because the user did not specify
individual columns.

Mark a query ambiguous only when missing information materially affects
the intended meaning or prevents a reliable query from being constructed.

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
        "Show me all students.",
        "How many students are there?",
        "Show me students from the Computer Science department.",
        "Show me the top students.",
        "Show me students from the department.",
        "Show me courses with high credits.",
        "Show me all courses."
    ]

    for question in questions:

        print("\n" + "=" * 80)
        print("QUESTION:", question)
        print("=" * 80)

        result = analyze_query(question)

        print(result.model_dump_json(indent=2))