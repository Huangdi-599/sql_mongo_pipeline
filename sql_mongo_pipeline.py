import sqlglot
from sqlglot.expressions import Join, Group, Order, Limit, Select, CTE, Where
from utils import parse_condition, parse_aggregate_function
from datetime import datetime

def create_temp_collection_name(cte_name):
    """Create a unique temporary collection name for CTE results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"temp_{cte_name}_{timestamp}"

def sql_to_mongo_pipeline(sql: str) -> dict:
    ast = sqlglot.parse_one(sql)
    
    # Handle CTEs
    cte_collections = {}
    cte_block = ast.args.get("with")
    if cte_block:
        for cte in cte_block.expressions:
            name = cte.alias
            query = cte.this.sql()
            # Create a unique temporary collection name for this CTE
            temp_collection = create_temp_collection_name(name)
            # Process CTE and store its pipeline
            cte_pipeline = sql_to_mongo_pipeline(query)
            cte_collections[name] = {
                "temp_collection": temp_collection,
                "pipeline": cte_pipeline
            }

    # Get main query details
    main_table = ast.args["from"].name
    pipeline = []

    # If the main query references a CTE
    if main_table in cte_collections:
        # Use the CTE's temporary collection
        return {
            "collection": cte_collections[main_table]["temp_collection"],
            "pipeline": [],
            "cte_collections": cte_collections
        }
    
    # Handle JOINs
    join = ast.find(Join)
    if join:
        right_table = join.this.name
        on = join.args["on"]
        left_field = on.left.sql().split(".")[1]
        right_field = on.right.sql().split(".")[1]

        # If joining with a CTE
        if right_table in cte_collections:
            # Use $lookup with the CTE's temporary collection
            pipeline.append({
                "$lookup": {
                    "from": cte_collections[right_table]["temp_collection"],
                    "localField": left_field,
                    "foreignField": right_field,
                    "as": right_table
                }
            })
        else:
            # Normal collection join
            pipeline.append({
                "$lookup": {
                    "from": right_table,
                    "localField": left_field,
                    "foreignField": right_field,
                    "as": right_table
                }
            })
        pipeline.append({ "$unwind": f"${right_table}" })

    # WHERE
    where = ast.find(Where)
    if where:
        match_stage = parse_condition(where.this)
        pipeline.append({ "$match": match_stage })

    # GROUP BY
    group = ast.find(Group)
    if group:
        group_fields = group.expressions
        _id = {}
        for col in group_fields:
            col_name = col.name
            _id[col_name] = f"${col_name}"

        group_stage = {"_id": _id}
        for expr in ast.selects:
            alias = expr.alias_or_name
            agg = parse_aggregate_function(expr)
            if agg:
                group_stage[alias] = agg

        pipeline.append({ "$group": group_stage })

    # ORDER BY
    order = ast.find(Order)
    if order:
        sort = {}
        for o in order.expressions:
            sort[o.this.name] = -1 if o.args.get("desc") else 1
        pipeline.append({ "$sort": sort })

    # LIMIT
    limit = ast.find(Limit)
    if limit:
        pipeline.append({ "$limit": int(limit.expression.name) })

    return {
        "collection": main_table,
        "pipeline": pipeline,
        "cte_collections": cte_collections
    }

def execute_mongo_query(db, query_result):
    """Execute the MongoDB query with CTE support using temporary collections"""
    try:
        # First execute all CTEs and store results in temporary collections
        if "cte_collections" in query_result:
            for cte_name, cte_info in query_result["cte_collections"].items():
                # Execute CTE pipeline
                cte_results = list(db[cte_info["pipeline"]["collection"]].aggregate(
                    cte_info["pipeline"]["pipeline"]
                ))
                
                # Create temporary collection and insert results
                temp_collection = cte_info["temp_collection"]
                if cte_results:
                    db[temp_collection].insert_many(cte_results)
        
        # Execute main query
        collection = db[query_result["collection"]]
        results = list(collection.aggregate(query_result["pipeline"]))
        
        return results
    
    finally:
        # Clean up temporary collections
        if "cte_collections" in query_result:
            for cte_info in query_result["cte_collections"].values():
                db[cte_info["temp_collection"]].drop()
