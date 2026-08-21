from schema import schema


def validate_column(column, errors):

    if column == "*":
        return

    if "." not in column:

        errors.append({
            "type": "invalid_column_reference",
            "column": column,
            "message": (
                f"Column '{column}' must be fully qualified."
            )
        })

        return

    table_name, column_name = column.split(".", 1)

    if table_name not in schema:

        errors.append({
            "type": "missing_table",
            "table": table_name,
            "message": (
                f"Table '{table_name}' does not exist."
            )
        })

        return

    if column_name not in schema[table_name]["columns"]:

        errors.append({
            "type": "missing_column",
            "column": column,
            "message": (
                f"Column '{column}' does not exist "
                f"in table '{table_name}'."
            )
        })


def validate_query_analysis(query_analysis):

    errors = []

    # --------------------------------------------------
    # Validate tables
    # --------------------------------------------------

    for table in query_analysis.tables:

        if table not in schema:

            errors.append({
                "type": "missing_table",
                "table": table,
                "message": (
                    f"Table '{table}' does not exist "
                    "in the database schema."
                )
            })

    # --------------------------------------------------
    # Validate SELECT columns
    # --------------------------------------------------

    for column in query_analysis.selected_columns:

        validate_column(
            column,
            errors
        )

    # --------------------------------------------------
    # Validate filters
    # --------------------------------------------------

    for filter_item in query_analysis.filters:

        validate_column(
            filter_item.column,
            errors
        )

    # --------------------------------------------------
    # Validate aggregations
    # --------------------------------------------------

    for aggregation in query_analysis.aggregations:

        validate_column(
            aggregation.column,
            errors
        )

    # --------------------------------------------------
    # Validate GROUP BY
    # --------------------------------------------------

    for column in query_analysis.group_by:

        validate_column(
            column,
            errors
        )

    # --------------------------------------------------
    # Validate ORDER BY
    # --------------------------------------------------

    for order in query_analysis.order_by:

        validate_column(
            order.column,
            errors
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


if __name__ == "__main__":

    from query_analyzer import analyze_query

    question = input(
        "Enter a question: "
    )

    analysis = analyze_query(
        question
    )

    print("\nQuery Analysis:")

    print(
        analysis.model_dump_json(
            indent=2
        )
    )

    result = validate_query_analysis(
        analysis
    )

    print("\nValidation Result:")

    print(result)