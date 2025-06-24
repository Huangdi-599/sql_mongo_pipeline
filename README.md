# SQL to MongoDB Aggregation Pipeline

[![Build Status](https://github.com/Huangdi-599/sql_mongo_pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/Huangdi-599/sql_mongo_pipeline/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/sql-mongo-pipeline.svg)](https://badge.fury.io/py/sql-mongo-pipeline)

This project is a Python-based tool that translates SQL queries into MongoDB aggregation pipelines. It leverages the `sqlglot` library to parse SQL queries and dynamically construct the corresponding MongoDB aggregation stages. This allows developers who are more familiar with SQL to interact with MongoDB databases using a familiar query language.

## Features

- **SQL to MongoDB Aggregation:** Automatically converts SQL queries into MongoDB aggregation pipelines.
- **Supported SQL Clauses:**
    - `SELECT`
    - `FROM`
    - `JOIN` (LEFT JOIN)
    - `WHERE`
    - `GROUP BY`
    - `ORDER BY`
    - `LIMIT`
- **CTE (Common Table Expression) Support:** Handles CTEs by creating temporary collections for intermediate results.
- **Extensible:** The modular design allows for the addition of more SQL features and clauses.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Huangdi-599/sql_mongo_pipeline.git
    cd sql_mongo_pipeline
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv env
    source env/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Here's a simple example of how to use the `sql_to_mongo_pipeline` function:

```python
from sql_mongo_pipeline import sql_to_mongo_pipeline, execute_mongo_query
from pymongo import MongoClient

# Connect to your MongoDB database
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']

# Example SQL query
sql_query = """
WITH regional_sales AS (
    SELECT region, SUM(amount) AS total_sales
    FROM sales
    GROUP BY region
)
SELECT r.region, r.total_sales
FROM regional_sales r
JOIN regions reg ON r.region = reg.name
WHERE r.total_sales > 1000
ORDER BY r.total_sales DESC
LIMIT 5
"""

# Convert SQL to MongoDB pipeline
mongo_query = sql_to_mongo_pipeline(sql_query)

# Execute the query
results = execute_mongo_query(db, mongo_query)

# Print the results
for doc in results:
    print(doc)

## CLI Usage

After installing the package (e.g., with `pip install -e .`), you can use the `sql-mongo-pipeline` command-line tool:

- **Convert SQL to MongoDB pipeline (print as JSON):**
  ```bash
  sql-mongo-pipeline --sql "SELECT * FROM users WHERE age > 30"
  ```

- **Convert SQL from a file:**
  ```bash
  sql-mongo-pipeline --sql-file path/to/query.sql
  ```

- **Pretty-print the output:**
  ```bash
  sql-mongo-pipeline --sql "SELECT * FROM users" --pretty
  ```

- **Execute the pipeline on MongoDB and print results:**
  ```bash
  sql-mongo-pipeline --sql "SELECT * FROM users" --run --mongo-uri "mongodb://localhost:27017/" --mongo-db test_db
  ```

Use `sql-mongo-pipeline --help` for all options.

## How it Works

The script uses `sqlglot` to parse the input SQL query into an Abstract Syntax Tree (AST). It then traverses the AST to identify different SQL clauses and constructs the equivalent MongoDB aggregation stages.

- **CTEs:** CTEs are processed first, and their results are stored in temporary collections. These temporary collections are then used in the main query.
- **JOINs:** `JOIN` operations are converted to `$lookup` stages.
- **WHERE:** `WHERE` clauses are converted to `$match` stages.
- **GROUP BY:** `GROUP BY` clauses are converted to `$group` stages with corresponding accumulators for aggregate functions like `SUM`, `AVG`, etc.
- **ORDER BY:** `ORDER BY` clauses are converted to `$sort` stages.
- **LIMIT:** `LIMIT` clauses are converted to `$limit` stages.

## Supported SQL Features
- SELECT, FROM
- WHERE
- JOIN (LEFT JOIN)
- GROUP BY
- ORDER BY
- LIMIT
- CTE (WITH ... AS ...)

**Planned/Partial Support:**
- HAVING
- DISTINCT
- Subqueries
- UNION

## Contributing & Community

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started.

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 