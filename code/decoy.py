import random
import names

# This file is for generating decoy data. It's supposed to represent data in superposition


# Function to generate valid name decoys by modifying the original name
def generate_valid_name_decoys(name, num_decoys=5):
    decoys = set()

    while len(decoys) < num_decoys:
        # Generate a random name and check if it's similar to the original
        new_name = names.get_first_name()

        # Check if new name is phonetically or visually close
        if new_name[0] == name[0] and len(new_name) in range(
            len(name) - 1, len(name) + 2
        ):
            decoys.add(new_name)

    return list(decoys)


# Example usage
original_name = "John"
decoy_names = generate_valid_name_decoys(original_name)
print(f"Original name: {original_name}")
print(f"Valid decoys: {decoy_names}")
