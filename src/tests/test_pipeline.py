import pytest
from sql_mongo_pipeline import sql_to_mongo_pipeline

# Test Case 1: Basic SELECT with WHERE and ORDER BY
def test_basic_select_where_order():
    """Test SELECT with WHERE and ORDER BY."""
    sql = """
    SELECT name, email, age 
    FROM users 
    WHERE age > 30 AND active = TRUE 
    ORDER BY age DESC;
    """
    pipeline = sql_to_mongo_pipeline(sql)
    assert pipeline["collection"] == "users"
    assert any(stage.get("$match") for stage in pipeline["pipeline"])
    assert any(stage.get("$sort") for stage in pipeline["pipeline"])

# Test Case 2: Aggregation with GROUP BY
def test_group_by():
    """Test GROUP BY aggregation."""
    sql = """
    SELECT status, COUNT(*) as order_count
    FROM orders
    GROUP BY status;
    """
    pipeline = sql_to_mongo_pipeline(sql)
    assert pipeline["collection"] == "orders"
    assert any("$group" in stage for stage in pipeline["pipeline"])

# Test Case 3: JOIN
def test_join():
    """Test JOIN between users and orders."""
    sql = """
    SELECT u.name, o.amount
    FROM users u
    JOIN orders o ON u.id = o.user_id;
    """
    pipeline = sql_to_mongo_pipeline(sql)
    assert any("$lookup" in stage for stage in pipeline["pipeline"])

# Test Case 4: CTE
def test_cte():
    """Test CTE support."""
    sql = """
    WITH user_stats AS (
        SELECT user_id, COUNT(*) as order_count
        FROM orders
        GROUP BY user_id
    )
    SELECT * FROM user_stats;
    """
    pipeline = sql_to_mongo_pipeline(sql)
    assert "cte_collections" in pipeline

# Test Case 5: LIMIT
def test_limit():
    """Test LIMIT clause."""
    sql = """
    SELECT * FROM users LIMIT 10;
    """
    pipeline = sql_to_mongo_pipeline(sql)
    assert any("$limit" in stage for stage in pipeline["pipeline"])