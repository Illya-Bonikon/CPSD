from pymongo import MongoClient
import datetime

class MongoLogger:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="tsp_lab5"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.runs = self.db["runs"]

    def save_run(self, graph, params, generations_stats):
        doc = {
            "datetime": datetime.datetime.now(),
            "graph": graph.tolist(),
            "params": params,
            "generations": generations_stats
        }
        return self.runs.insert_one(doc).inserted_id 