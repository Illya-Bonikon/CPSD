from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from ..db.mongodb import mongodb
from ..models.algorithm_run import AlgorithmRunCreate, AlgorithmRun, AlgorithmRunInDB
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

settings = get_settings()
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]
collection = db.algorithm_runs

async def create_algorithm_run(run: AlgorithmRunCreate) -> AlgorithmRun:
    run_dict = run.model_dump()
    run_dict["status"] = "running"
    run_dict["start_time"] = datetime.utcnow()
    run_dict["current_generation"] = 0
    result = await collection.insert_one(run_dict)
    created_run = await get_algorithm_run(str(result.inserted_id))
    return created_run

async def get_algorithm_run(run_id: str) -> Optional[AlgorithmRun]:
    if not ObjectId.is_valid(run_id):
        return None
    run = await collection.find_one({"_id": run_id})
    return AlgorithmRun(**run) if run else None

async def get_algorithm_runs(
    skip: int = 0,
    limit: int = 100,
    graph_id: Optional[str] = None,
    status: Optional[str] = None
) -> List[AlgorithmRun]:
    query = {}
    if graph_id:
        query["graph_id"] = graph_id
    if status:
        query["status"] = status
    
    cursor = collection.find(query).skip(skip).limit(limit)
    runs = await cursor.to_list(length=limit)
    return [AlgorithmRun(**run) for run in runs]

async def update_algorithm_run(run_id: str, update_data: dict) -> Optional[AlgorithmRun]:
    if not ObjectId.is_valid(run_id):
        return None
    
    if "status" in update_data and update_data["status"] == "completed":
        update_data["end_time"] = datetime.utcnow()
    
    result = await collection.update_one(
        {"_id": run_id},
        {"$set": update_data}
    )
    if result.modified_count:
        updated_run = await get_algorithm_run(run_id)
        return updated_run
    return None

async def delete_algorithm_run(run_id: str) -> bool:
    if not ObjectId.is_valid(run_id):
        return False
    result = await collection.delete_one({"_id": run_id})
    return result.deleted_count > 0

async def get_running_runs() -> List[AlgorithmRun]:
    runs = await collection.find({"status": "running"}).to_list(length=None)
    return [AlgorithmRun(**run) for run in runs]

async def get_graph_runs(graph_id: str, status: Optional[str] = None) -> List[AlgorithmRun]:
    if not ObjectId.is_valid(graph_id):
        return []
    
    query = {"graph_id": ObjectId(graph_id)}
    if status:
        query["status"] = status
    
    runs = await collection.find(query).to_list(length=None)
    return [AlgorithmRun(**run) for run in runs]

async def update_algorithm_run_status(run_id: str, update_data: Dict[str, Any]) -> Optional[AlgorithmRun]:
    if "status" not in update_data:
        raise ValueError("Status is required for update")
    
    allowed_statuses = ["running", "paused", "completed", "failed"]
    if update_data["status"] not in allowed_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(allowed_statuses)}")
    
    if update_data["status"] == "completed":
        update_data["end_time"] = datetime.utcnow()
    
    result = await collection.update_one(
        {"_id": run_id},
        {"$set": update_data}
    )
    
    if result.modified_count > 0:
        return await get_algorithm_run(run_id)
    return None 