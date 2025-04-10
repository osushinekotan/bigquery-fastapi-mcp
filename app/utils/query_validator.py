import sqlparse


def is_read_only_query(query: str) -> tuple[bool, str]:
    """
    Validates if the query is read-only by checking for DML or DDL statements

    Args:
        query (str): The SQL query to validate

    Returns:
        Tuple[bool, str]: (is_valid, reason)
    """
    statements = sqlparse.parse(query)
    if not statements:
        return False, "No valid SQL statement found"

    # Check first statement type
    first_statement = statements[0]
    first_token = first_statement.token_first(skip_ws=True, skip_cm=True)

    if not first_token:
        return False, "No valid SQL tokens found"

    # DML/DDL operations that are not read-only
    forbidden_operations = {
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "MERGE",
        "REPLACE",
        "GRANT",
        "REVOKE",
    }

    if first_token.value.upper() in forbidden_operations:
        return False, f"Operation '{first_token.value}' is not allowed"

    parsed = sqlparse.parse(query)
    for statement in parsed:
        for token in statement.flatten():
            if token.ttype not in (
                sqlparse.tokens.Whitespace,
                sqlparse.tokens.Comment.Single,
                sqlparse.tokens.Comment.Multiline,
            ):
                if token.value.upper() in forbidden_operations:
                    return False, f"Operation '{token.value}' is not allowed"

    return True, ""


def validate_dataset_references(query: str, allowed_datasets: set[str]) -> tuple[bool, str]:
    """
    Validates if the query only references allowed datasets

    Args:
        query (str): The SQL query to validate
        allowed_datasets (Set[str]): Set of allowed dataset names

    Returns:
        Tuple[bool, str]: (is_valid, reason)
    """
    if not allowed_datasets:
        return True, ""

    # Check if any other dataset references remain
    parsed = sqlparse.parse(query)
    for statement in parsed:
        for token in statement.flatten():
            if (token.ttype) in (None, sqlparse.tokens.Name) and "." in token.value:
                parts = token.value.strip("`").split(".")
                if len(parts) == 2 and parts[0] not in allowed_datasets:
                    return False, f"Reference to unauthorized dataset: {parts[0]}"
                elif len(parts) == 3 and parts[1] not in allowed_datasets:
                    return False, f"Reference to unauthorized dataset: {parts[1]}"

    return True, ""
