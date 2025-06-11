from typing import Any, Dict, Union
import sqlglot
from sqlglot.expressions import Condition, Column, Literal, Expression

def parse_literal(expr: Expression) -> Any:
    if isinstance(expr, Literal):
        val = expr.this
        if expr.is_string:
            return val.strip("'\"")
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val
    return str(expr)
def parse_condition(expr: Expression) -> Dict[str, Any]:
    if expr is None:
        return {}

    if expr.args.get("op") in ("AND", "OR"):
        op = "$and" if expr.args["op"] == "AND" else "$or"
        return {
            op: [
                parse_condition(expr.args["this"]),
                parse_condition(expr.args["expression"])
            ]
        }

    op_map = {
        "EQ": "$eq",
        "GT": "$gt",
        "GTE": "$gte",
        "LT": "$lt",
        "LTE": "$lte",
        "NEQ": "$ne",
    }

    expr_type = expr.__class__.__name__
    if expr_type in op_map:
        left = expr.left.name if isinstance(expr.left, Column) else str(expr.left)
        right = parse_literal(expr.right)
        return {left: {op_map[expr_type]: right}}

    if isinstance(expr, Condition) and expr.this:
        return parse_condition(expr.this)

    return {}


def parse_aggregate_function(expr: Expression) -> Union[Dict[str, Any], None]:
    func_name = expr.name.upper()
    col_expr = expr.args.get("this")
    col = col_expr.name if isinstance(col_expr, Column) else None

    if func_name == "COUNT":
        return {"$sum": 1}
    if func_name == "SUM" and col:
        return {"$sum": f"${col}"}
    if func_name == "AVG" and col:
        return {"$avg": f"${col}"}
    if func_name == "MAX" and col:
        return {"$max": f"${col}"}
    if func_name == "MIN" and col:
        return {"$min": f"${col}"}
    return None
