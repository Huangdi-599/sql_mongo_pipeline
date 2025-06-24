import argparse
import json
from .pipeline import sql_to_mongo_pipeline, execute_mongo_query
from pymongo import MongoClient

def main():
    parser = argparse.ArgumentParser(
        description="Convert SQL to MongoDB aggregation pipeline or execute it."
    )
    parser.add_argument(
        "--sql", type=str, help="SQL query string. If omitted, --sql-file is required."
    )
    parser.add_argument(
        "--sql-file", type=str, help="Path to a file containing the SQL query."
    )
    parser.add_argument(
        "--mongo-uri", type=str, help="MongoDB URI (if you want to execute the pipeline)."
    )
    parser.add_argument(
        "--mongo-db", type=str, help="MongoDB database name (required if executing)."
    )
    parser.add_argument(
        "--run", action="store_true", help="Actually run the pipeline on MongoDB."
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print the output JSON."
    )
    args = parser.parse_args()

    if not args.sql and not args.sql_file:
        parser.error("You must provide --sql or --sql-file.")

    if args.sql:
        sql = args.sql
    else:
        with open(args.sql_file, "r") as f:
            sql = f.read()

    pipeline = sql_to_mongo_pipeline(sql)
    if args.pretty:
        print(json.dumps(pipeline, indent=2))
    else:
        print(json.dumps(pipeline))

    if args.run:
        if not args.mongo_uri or not args.mongo_db:
            parser.error("--mongo-uri and --mongo-db are required to run the pipeline.")
        client = MongoClient(args.mongo_uri)
        db = client[args.mongo_db]
        results = execute_mongo_query(db, pipeline)
        if args.pretty:
            print(json.dumps(results, indent=2, default=str))
        else:
            print(json.dumps(results, default=str))

if __name__ == "__main__":
    main() 