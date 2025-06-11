from sql_mongo_pipeline import sql_to_mongo_pipeline, execute_mongo_query
from pymongo import MongoClient
import json
from bson import json_util

# Test Case 1: Basic SELECT with WHERE and ORDER BY
sql1 = """
SELECT name, email, age 
FROM users 
WHERE age > 30 AND active = TRUE 
ORDER BY age DESC;
"""

# Test Case 2: Aggregation with GROUP BY and HAVING
sql2 = """
SELECT status, 
       COUNT(*) as order_count, 
       AVG(amount) as avg_amount
FROM orders 
GROUP BY status 
HAVING COUNT(*) > 50;
"""

# Test Case 3: Complex JOIN with multiple conditions
sql3 = """
SELECT u.name, 
       COUNT(o.id) as total_orders,
       SUM(o.amount) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.active = TRUE 
  AND o.status = 'delivered'
  AND o.created_at > '2024-01-01'
GROUP BY u.name
HAVING COUNT(o.id) > 2
ORDER BY total_spent DESC
LIMIT 5;
"""

# Test Case 4: Subquery in WHERE clause
sql4 = """
SELECT name, email
FROM users
WHERE id IN (
    SELECT user_id 
    FROM orders 
    WHERE amount > 400
);
"""

# Test Case 5: Multiple JOINs with different conditions
sql5 = """
SELECT u.name,
       COUNT(DISTINCT o.id) as order_count,
       MAX(o.amount) as highest_order
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = TRUE
GROUP BY u.name
ORDER BY order_count DESC;
"""

# Test Case 6: Simple CTE with basic aggregation
sql6 = """
WITH user_stats AS (
    SELECT user_id, 
           COUNT(*) as order_count,
           AVG(amount) as avg_order_value
    FROM orders
    GROUP BY user_id
)
SELECT u.name, 
       us.order_count,
       ROUND(us.avg_order_value, 2) as avg_order_value
FROM users u
JOIN user_stats us ON u.id = us.user_id
WHERE us.order_count > 5
ORDER BY us.avg_order_value DESC;
"""

# Test Case 7: Multiple CTEs with complex logic
sql7 = """
WITH recent_orders AS (
    SELECT user_id, amount, created_at
    FROM orders
    WHERE status = 'delivered'
    AND created_at > '2024-01-01'
),
high_value_orders AS (
    SELECT user_id, 
           COUNT(*) as high_value_count,
           SUM(amount) as total_high_value
    FROM recent_orders
    WHERE amount > 300
    GROUP BY user_id
)
SELECT u.name,
       COALESCE(hvo.high_value_count, 0) as high_value_orders,
       COALESCE(hvo.total_high_value, 0) as total_high_value_amount
FROM users u
LEFT JOIN high_value_orders hvo ON u.id = hvo.user_id
WHERE u.active = TRUE
ORDER BY hvo.total_high_value DESC
LIMIT 10;
"""

# Test Case 8: Simple CTE with SELECT *
sql8 = """
WITH active_users AS (
    SELECT *
    FROM users
    LIMIT 5
)
SELECT *
FROM active_users;
"""

# Test Case 9: CTE with SELECT * and WHERE
sql9 = """
WITH recent_orders AS (
    SELECT *
    FROM orders
    WHERE status = 'delivered'
    LIMIT 10
)
SELECT *
FROM recent_orders;
"""

# Test Case 10: Multiple CTEs with SELECT *
sql10 = """
WITH active_users AS (
    SELECT *
    FROM users
    WHERE active = TRUE
    LIMIT 3
),
user_orders AS (
    SELECT *
    FROM orders
    LIMIT 5
)
SELECT *
FROM active_users;
"""

def run_test(sql, test_name):
    print(f"\n{'='*50}")
    print(f"Running Test: {test_name}")
    print(f"{'='*50}")
    
    # Convert SQL to MongoDB pipeline
    mongo_query = sql_to_mongo_pipeline(sql)
    print("\nMongoDB Pipeline:")
    print(json.dumps(mongo_query, indent=2))
    
    # Execute the pipeline
    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_db"]
    
    try:
        results = execute_mongo_query(db, mongo_query)
        print("\nResults:")
        print(json.dumps(results, indent=2, default=json_util.default))
    except Exception as e:
        print(f"Error executing query: {str(e)}")

# Run all tests
tests = [
    # (sql1, "Basic SELECT with WHERE and ORDER BY"),
    # (sql2, "Aggregation with GROUP BY and HAVING"),
    # (sql3, "Complex JOIN with multiple conditions"),
    # (sql4, "Subquery in WHERE clause"),
    # (sql5, "Multiple JOINs with different conditions"),
    # (sql6, "Simple CTE with basic aggregation"),
    # (sql7, "Multiple CTEs with complex logic"),
    # (sql8, "Simple CTE with SELECT *"),
    # (sql9, "CTE with SELECT * and WHERE"),
    # (sql10, "Multiple CTEs with SELECT *")
]

for sql, test_name in tests:
    run_test(sql, test_name)