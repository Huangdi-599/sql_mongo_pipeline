from pymongo import MongoClient
import random
from datetime import datetime, timedelta
import faker

def init_test_mongodb(uri="your_atlas_connection_string"):
    # Create client with SSL settings
    client = MongoClient(uri, 
                        tls=True,
                        tlsAllowInvalidCertificates=True)
    db = client["test_db"]

    # Clear existing data
    db.users.delete_many({})
    db.orders.delete_many({})

    fake = faker.Faker()

    # Create users
    users = []
    for user_id in range(1, 51):
        user = {
            "id": user_id,
            "name": fake.name(),
            "email": fake.email(),
            "age": random.randint(18, 60),
            "signup_date": datetime.combine(fake.date_between(start_date='-3y', end_date='today'), datetime.min.time()),
            "active": random.choice([True, False])
        }
        users.append(user)
    db.users.insert_many(users)

    # Create orders
    orders = []
    for _ in range(300):
        user_id = random.randint(1, 50)
        order = {
            "user_id": user_id,
            "amount": round(random.uniform(20.0, 500.0), 2),
            "item": fake.word(),
            "status": random.choice(["shipped", "delivered", "pending", "cancelled"]),
            "created_at": datetime.now() - timedelta(days=random.randint(0, 730))
        }
        orders.append(order)
    db.orders.insert_many(orders)

    print("✅ MongoDB test data initialized in 'test_db' with 'users' and 'orders' collections.")

if __name__ == "__main__":
    init_test_mongodb()
    # You can specify a different URI if needed
    # init_test_mongodb("mongodb://your_custom_uri:27017/")
