from django.http import JsonResponse
from pymongo import MongoClient
from .pipeline import sql_to_mongo_pipeline

client = MongoClient("mongodb://localhost:27017/")
mongo_db = client["your_database_name"]

def run_sql_query(request) -> JsonResponse:
    """
    Django view to run a SQL query and return MongoDB results as JSON.
    Args:
        request: Django HTTP request object.
    Returns:
        JsonResponse with query results or error.
    """
    if request.method == "POST":
        sql = request.POST.get("sql")

        try:
            result = sql_to_mongo_pipeline(sql)
            collection = result["collection"]
            pipeline = result["pipeline"]

            data = list(mongo_db[collection].aggregate(pipeline))
            return JsonResponse({"data": data}, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)
