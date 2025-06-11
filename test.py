from sql_mongo import sql_to_mongo_pipeline
sql = """
WITH recent_orders AS (
  SELECT user_id, amount, created_at
  FROM orders
  WHERE created_at >= '2024-01-01'
)
SELECT u.name, COUNT(ro.amount) AS order_count, SUM(ro.amount) AS total_spent
FROM users u
JOIN recent_orders ro ON u.id = ro.user_id
WHERE u.active = TRUE
GROUP BY u.name
ORDER BY total_spent DESC
LIMIT 10;
"""

result = sql_to_mongo_pipeline(sql)
print(result)
