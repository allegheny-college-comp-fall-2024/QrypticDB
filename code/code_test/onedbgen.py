import random
import uuid

# Number of records (change for more)
num_customers = 20000  # 5000  # Start small, increase as needed
num_orders = 10000
num_products = 5000

# Sample data for random selection
first_names = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Emily",
    "Frank",
    "Grace",
    "Hannah",
    "Isaac",
    "Jack",
    "Katherine",
    "Liam",
    "Mia",
    "Nathan",
    "Olivia",
    "Peter",
    "Quinn",
    "Rachel",
    "Samuel",
    "Taylor",
    "Ursula",
    "Victor",
    "Wendy",
    "Xavier",
    "Yasmine",
    "Zachary",
    "Aaron",
    "Brandon",
    "Catherine",
    "Derek",
    "Eleanor",
    "Felix",
    "Gabriella",
    "Henry",
    "Isabella",
    "Jacob",
    "Kevin",
    "Laura",
    "Michael",
    "Natalie",
    "Owen",
    "Penelope",
    "Quincy",
    "Raymond",
    "Sophia",
    "Theodore",
    "Ulysses",
    "Vanessa",
    "Walter",
    "Xena",
    "Yvonne",
    "Zane",
]

last_names = [
    "Johnson",
    "Smith",
    "Brown",
    "Wilson",
    "Davis",
    "Anderson",
    "Clark",
    "Martinez",
    "Taylor",
    "Harris",
    "Garcia",
    "Robinson",
    "Walker",
    "Lewis",
    "Young",
    "Allen",
    "King",
    "Scott",
    "Adams",
    "Nelson",
    "Baker",
    "Hall",
    "Mitchell",
    "Carter",
    "Perez",
    "Roberts",
    "Evans",
    "Campbell",
    "Edwards",
    "Collins",
    "Stewart",
    "Morris",
    "Nguyen",
    "Murphy",
    "Rogers",
    "Cook",
    "Morgan",
    "Bell",
    "Reed",
    "Bailey",
    "Cooper",
    "Richardson",
    "Cox",
    "Howard",
    "Ward",
    "Torres",
    "Peterson",
    "Gray",
    "Ramirez",
    "James",
    "Watson",
    "Brooks",
    "Kelly",
    "Sanders",
    "Price",
    "Bennett",
    "Wood",
    "Barnes",
    "Ross",
    "Henderson",
]

domains = [
    "example.com",
    "test.com",
    "mail.com",
    "secure.com",
    "company.com",
    "business.net",
    "webmail.org",
    "techmail.io",
    "cloudhost.com",
    "fastmail.net",
    "myemail.org",
    "privatebox.com",
    "cybersecure.net",
    "trustedmail.io",
    "protonmail.com",
    "mailservice.org",
    "useremail.net",
    "fastsecure.io",
    "networkmail.com",
    "safemail.org",
    "encryptmail.net",
]

customers = []
existing_customer_ids = set()
for _ in range(num_customers):
    customer_id = len(existing_customer_ids) + 1
    customer_name = f"{random.choice(['Alice', 'Bob', 'Charlie', 'David', 'Emily'])} {uuid.uuid4().hex[:7]}"
    email = f"{customer_name.replace(' ', '.').lower()}@example.com"
    phone = f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    address = f"{random.randint(1, 9999)} {random.choice(['Main St', 'Oak St', 'Pine St', 'Maple St'])}, City {uuid.uuid4().hex[:6]}"
    customers.append(
        f"INSERT INTO Customers (customer_id, name, email, phone, address) VALUES ({customer_id}, '{customer_name}', '{email}', '{phone}', '{address}');"
    )
    existing_customer_ids.add(customer_id)

# Generate unique orders
orders = []
existing_order_ids = set()
for _ in range(num_orders):
    order_id = len(existing_order_ids) + 1
    # if customer_id not in existing_customer_ids:
    #     # Generate and insert a new customer with the given customer_id
    #     customer_name = f"{random.choice(['Alice', 'Bob', 'Charlie', 'David', 'Emily'])} {uuid.uuid4().hex[:4]}"
    #     email = f"{customer_name.replace(' ', '.').lower()}@example.com"
    #     phone = f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    #     address = f"{random.randint(1, 9999)} {random.choice(['Main St', 'Oak St', 'Pine St', 'Maple St'])}, City {uuid.uuid4().hex[:6]}"
    #     customers.append(
    #         f"INSERT INTO Customers (customer_id, name, email, phone, address) VALUES ({}, '{customer_name}', '{email}', '{phone}', '{address}');"
    #     )
    #     existing_order_ids.add(customer_id)

    total_amount = round(random.uniform(10, 1000), 2)
    status = random.choice(["Pending", "Shipped", "Delivered", "Cancelled"])
    orders.append(
        f"INSERT INTO Orders (order_id, total_amount, status) VALUES ({order_id}, {total_amount}, '{status}');"
    )
    existing_order_ids.add(order_id)
    # order_id SERIAL PRIMARY KEY, total_amount DECIMAL(10,2) NULL, status VARCHAR DEFAULT 'Pending';",

# Generate unique products
products = []
existing_product_ids = set()
for _ in range(num_products):
    product_id = len(existing_product_ids) + 1
    product_name = f"Product {uuid.uuid4().hex[:6]}"  # Unique product names
    price = round(random.uniform(5, 500), 2)
    stock = random.randint(10, 1000)
    products.append(
        f"INSERT INTO Products (product_id, name, price, stock) VALUES ({product_id}, '{product_name}', {price}, {stock});"
    )
    existing_product_ids.add(product_id)

# all_queries = customers + orders + products

# # Shuffle the combined list to randomize the order
# random.shuffle(all_queries)
# Save queries to a file
with open("encryption_test_data.csv", "w") as f:
    f.write("\n".join(customers))

with open("or.csv", "w") as f:
    f.write("\n".join(orders))


with open("pr.csv", "w") as f:
    f.write("\n".join(products))


# print(
#     f"Generated {len(customers)} customers, {len(orders)} orders, and {len(products)} products."
# )
