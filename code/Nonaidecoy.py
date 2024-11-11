import re
import pandas as pd
import random
import string


def query_parse(query: str):
    # Ensure the input is a string
    if not isinstance(query, str):
        raise TypeError("Expected a string for 'query', but got a different data type.")

    # Clean up whitespace in the query
    query = " ".join(query.strip().split())

    # Extract the table name
    table_pattern = r"INSERT\s+INTO\s+(\w+)"
    table_match = re.search(table_pattern, query)
    table_name = table_match.group(1) if table_match else None

    # Extract column names
    column_pattern = r"INSERT\s+INTO\s+\w+\s*\((.*?)\)"
    column_match = re.search(column_pattern, query)
    columns = []
    if column_match:
        columns = [col.strip() for col in column_match.group(1).split(",")]
    else:
        raise ValueError("Error: No column names provided in the query.")

    # Extract values
    values_pattern = r"VALUES\s*(\(.*?\))"
    values_matches = re.finditer(values_pattern, query)
    all_values = []
    for match in values_matches:
        value_set = match.group(1).strip("()")
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        for char in value_set:
            if char in ["'", '"'] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
            elif char == "," and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char
        if current_value:
            values.append(current_value.strip())
        values = [v.strip().strip("'\"") for v in values]
        all_values.append(values)

    # Create DataFrame with extracted values
    df = pd.DataFrame(all_values, columns=columns)
    return {
        "table": table_name,
        "columns": columns,
        "values": all_values,
        "dataframe": df,
    }


def generate_decoys_from_query(parsed_data, num_decoys=10):
    decoy_data = {}

    for column in parsed_data["columns"]:
        real_value = parsed_data["dataframe"][column][
            0
        ]  # Assume first row contains the real data
        decoys = []

        # Pattern decoy generation
        if re.match(r"^\d+$", real_value):  # number values example: ages
            real_number = int(real_value)
            decoys = [
                str(real_number + random.randint(-10, 10)) for _ in range(num_decoys)
            ]
        # GPT
        elif re.match(
            r"^\d{3}-\d{3}-\d{4}$", real_value
        ):  # Strict "XXX-XXX-XXXX" format for phone numbers

            def random_phone():
                return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

            decoys = [random_phone() for _ in range(num_decoys)]

        elif re.match(
            r"^[\d-]+$", real_value
        ):  # Flexible pattern for string-numbers with hyphens

            def similar_string_number(value):
                parts = value.split("-")
                new_parts = [
                    str(random.randint(100, 999))[: len(part)] for part in parts
                ]
                return "-".join(new_parts)

            decoys = [similar_string_number(real_value) for _ in range(num_decoys)]

        elif re.match(
            r"^[a-zA-Z]+$", real_value
        ):  # Simple alphabetic strings (e.g., names, roles)

            def similar_name(name):
                return "".join(random.choices(string.ascii_lowercase, k=len(name)))

            decoys = [similar_name(real_value) for _ in range(num_decoys)]

        elif re.match(
            r"^[a-zA-Z\s]+$", real_value
        ):  # Multi-word alphabetic strings (e.g., job titles)

            def similar_text(text):
                words = text.split()
                new_words = [
                    "".join(random.choices(string.ascii_lowercase, k=len(word)))
                    for word in words
                ]
                return " ".join(new_words)

            decoys = [similar_text(real_value) for _ in range(num_decoys)]

        else:  # Default for unrecognized patterns (uses a random character sequence)
            decoys = [
                "".join(
                    random.choices(
                        string.ascii_letters + string.digits, k=len(real_value)
                    )
                )
                for _ in range(num_decoys)
            ]

        decoy_data[column] = decoys

    return decoy_data


# Function to concatenate real and decoy values into a single entry
def concatenate_with_decoys(real_value, decoys):
    # Combine real value with decoys, separated by commas
    return f"{real_value}," + ",".join(decoys)


# Example of parsing, generating decoys, and creating the modified query
def generate_insert_with_decoys(query: str, parsed_data, num_decoys=10):
    # Generate decoys for each column based on the real values
    decoy_results = generate_decoys_from_query(parsed_data, num_decoys)

    # Prepare modified values with real values and decoys
    modified_values = []
    for column, real_value in zip(parsed_data["columns"], parsed_data["values"][0]):
        # Get the generated decoys for this column
        decoys = decoy_results.get(column, [])
        # Concatenate the real value with its decoys
        combined_value = concatenate_with_decoys(real_value, decoys)
        modified_values.append(combined_value)

    # Format the modified values back into an SQL insert statement
    columns_str = ", ".join(parsed_data["columns"])
    values_str = "', '".join(modified_values)
    modified_query = (
        f"INSERT INTO {parsed_data['table']} ({columns_str}) VALUES ('{values_str}');"
    )

    return modified_query


