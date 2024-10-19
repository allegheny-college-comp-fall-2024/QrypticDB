import openai


def identify_and_generate_similar(input_string: str, decoy_amount: int):
    # Replace 'your-api-key' with your actual OpenAI API key
    openai.api_key = "your-api-key"

    # Step 1: Generalized prompt to generate decoys based on any input
    identification_prompt = f"""
        You will be provided with a SQL query. Your task is to:
        1. Identify the value being inserted into the database from the query.
        2. Generate {decoy_amount} similar values to the identified value.
        3. Return these values as a comma-separated Python list.

        Only generate real-world values similar to the one in the SQL query, whether it's a name, number, address, or anything else.
        Ensure the generated values are realistic, valid, and useful.

        Example input: {input_string}
        """

    # Call OpenAI API to generate decoy values
    identification_response = openai.Completion.create(
        engine="gpt-4",  # or "gpt-3.5-turbo"
        prompt=identification_prompt,
        max_tokens=150,
        temperature=0.7,
        n=1,
    )

    # Get the generated decoys as a comma separated list
    generated_decoys = identification_response.choices[0].text.strip()

    # Convert the comma separated string into a Python list
    decoy_list = [decoy.strip() for decoy in generated_decoys.split(",")]

    return decoy_list


input_query = (
    "INSERT INTO employees (name, age, address) VALUES ('John Doe', 35, '123 Main St');"
)
decoys = identify_and_generate_similar(input_query, 5)
print(decoys)
