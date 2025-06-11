import sqlglot
from sqlglot.expressions import Table, Join, Condition, Column, Where, Group, Order, Limit, Select, CTE

def sql_to_mongo_pipeline(sql: str) -> dict:
    ast = sqlglot.parse_one(sql)

    # Handle CTEs
    cte_data = {}
    cte_block = ast.args.get("with")
    if cte_block:
        for cte in cte_block.expressions:
            name = cte.alias
            query = cte.this.sql()
            cte_data[name] = sql_to_mongo_pipeline(query)

    main_table = ast.args["from"].name
    pipeline = []

    # Handle JOINs
    join = ast.find(Join)
    if join:
        right_table = join.this.name
        on = join.args["on"]
        left_field = on.left.sql().split(".")[1]
        right_field = on.right.sql().split(".")[1]

        pipeline.append({
            "$lookup": {
                "from": right_table,
                "localField": left_field,
                "foreignField": right_field,
                "as": right_table
            }
        })
        pipeline.append({ "$unwind": f"${right_table}" })

    # Handle WHERE
    where = ast.find(Where)
    if where:
        condition = where.this.sql().replace("=", ":").replace("AND", ",").replace("TRUE", "true")
        try:
            filter_expr = eval(f"{{{condition}}}")  # very basic, use ast.literal_eval or proper parser in production
            pipeline.append({ "$match": filter_expr })
        except:
            pass

    # Handle GROUP BY
    group = ast.find(Group)
    if group:
        group_fields = [f"${col.name}" for col in group.expressions]
        project = ast.args["expressions"]
        agg_expr = {
            "_id": { f: f"${f}" for f in group_fields }
        }
        for proj in project:
            alias = proj.alias_or_name
            if proj.name.lower().startswith("count("):
                agg_expr[alias] = { "$sum": 1 }
            elif proj.name.lower().startswith("sum("):
                col = proj.name[4:-1]
                agg_expr[alias] = { "$sum": f"${col.strip()}" }

        pipeline.append({ "$group": agg_expr })

    # Handle ORDER BY
    order = ast.find(Order)
    if order:
        sort = {}
        for o in order.expressions:
            sort[o.this.name] = -1 if o.args.get("desc") else 1
        pipeline.append({ "$sort": sort })

    # Handle LIMIT
    limit = ast.find(Limit)
    if limit:
        pipeline.append({ "$limit": int(limit.expression.name) })

    return {
        "collection": main_table,
        "pipeline": pipeline,
        "cte_cache": cte_data
    }
