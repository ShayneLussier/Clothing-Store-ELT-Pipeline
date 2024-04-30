from faker import Faker
import random
from datetime import datetime, timedelta
import os
import uuid

from .files import fetch_product_data, read_json, append_to_json
from .rates import api_date, retrieve_inr_to_cad_rate, convert_to_cad

# -------------------- VALUES -------------------- #

START_DATE = datetime.strptime("2024-03-02", "%Y-%m-%d")
END_DATE = datetime.today()

JSON = "transactions.json"

# -------------------- FUNCTIONS -------------------- #

fake = Faker(locale='fr_CA')

def generate_quebec_address():
    while True:
        address = fake.address()
        # Check if the address contains "Québec" or "QC" to filter out non-Quebec addresses
        if "Québec" in address or "QC" in address:
            address = address.replace('\n', ', ')
            if "Suite" not in address and "Apt." not in address:
                return address

def generate_date(start_date=START_DATE, end_date=END_DATE):
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    random_date = (start_date + timedelta(days=random_days)).strftime("%Y%m%d")
    return random_date

def transaction_new_customer(product_data, max_id):
    customer_name = fake.name()
    num_items = random.randint(1, 5)
    date = generate_date()
    rate = retrieve_inr_to_cad_rate(api_date(date))
    data = {
        "id": uuid.uuid4().hex,
        "date": date,
        "store_id": int(f'1200{num_items}'),
        # returns the product_id and price of a random product in 'products.csv' for a random number of items
        "items": [
            {"product_id": chosen_product['ProductID'],
                "price": convert_to_cad(float(chosen_product['Price (INR)']), rate)}
            for chosen_product in [random.choice(product_data) for _ in range(num_items)]
        ],
        "customer": {
            "id": max_id[0] + 1,
            "name": customer_name,
            "email": (f"{''.join(customer_name.split())}@email.com"),
            "address": generate_quebec_address(),
            "phone": fake.phone_number(),
            "card_number": fake.credit_card_number()
        }
    }
    print(data)
    max_id[0] += 1
    append_to_json(JSON, data)

def transaction_returning_customer(product_data, max_id):
    num_items = random.randint(1, 5)

    if not os.path.exists(JSON):
        # If the file doesn't exist, create a new customer as in the transaction_new_customer function
        transaction_new_customer(product_data, max_id)
        return

    # Select a random customer from the JSON data
    json_data = read_json(JSON)
    existing_customer = random.choice(json_data)
    
    # Generate transaction data using the selected customer's details
    date = generate_date()
    rate = retrieve_inr_to_cad_rate(api_date(date))
    data = {
        "id": uuid.uuid4().hex,
        "date": date,
        "store_id": int(f'1200{num_items}'),
        # returns the product_id and price of a random product in 'products.csv' for a random number of items
        "items": [
            {"product_id": chosen_product['ProductID'],
                "price": convert_to_cad(float(chosen_product['Price (INR)']), rate)}
            for chosen_product in [random.choice(product_data) for _ in range(num_items)]
        ],
        "customer": {
            "id": existing_customer["customer"]["id"],
            "name": existing_customer["customer"]["name"],
            "email": existing_customer["customer"]["email"],
            "address": existing_customer["customer"]["address"],
            "phone": existing_customer["customer"]["phone"],
            "card_number": existing_customer["customer"]["card_number"]
        }
    }
    print(data)
    append_to_json(JSON, data)

def generate_fake_transaction(amount, max_customer_id):
    if os.path.exists(JSON):
        os.remove(JSON)
    max_id = [int(max_customer_id[0]["MAX_CUSTOMER_ID"]) if max_customer_id[0]["MAX_CUSTOMER_ID"] is not None else 0]
    product_data = fetch_product_data()
    for _ in range(amount):
        # Decide whether the customer will be a new or returning customer at an 25% return rate
        is_repeat_customer = random.choices([True, False], weights=[0.25, 0.75])[0]

        if is_repeat_customer:
            transaction_returning_customer(product_data, max_id)
        else:
            transaction_new_customer(product_data, max_id)