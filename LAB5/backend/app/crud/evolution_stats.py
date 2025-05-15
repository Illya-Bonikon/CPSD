from typing import List, Optional
from bson import ObjectId
from ..db.mongodb import mongodb
from ..models.evolution_stats import EvolutionStatsCreate, EvolutionStats, EvolutionStatsInDB
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

settings = get_settings()
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]
collection = db.evolution_stats

async def create_evolution_stats(stats: EvolutionStatsCreate) -> EvolutionStats:
    stats_dict = stats.model_dump()
    result = await collection.insert_one(stats_dict)
    created_stats = await get_evolution_stats(str(result.inserted_id))
    return created_stats

async def get_evolution_stats(stats_id: str) -> Optional[EvolutionStats]:
    if not ObjectId.is_valid(stats_id):
        return None
    stats = await collection.find_one({"_id": stats_id})
    return EvolutionStats(**stats) if stats else None

async def get_run_evolution_stats(run_id: str) -> Optional[EvolutionStats]:
    if not ObjectId.is_valid(run_id):
        return None
    stats = await collection.find_one({"run_id": ObjectId(run_id)})
    return EvolutionStats(**stats) if stats else None

async def get_all_stats(
    skip: int = 0,
    limit: int = 100,
    run_id: Optional[str] = None
) -> List[EvolutionStats]:
    query = {}
    if run_id:
        query["run_id"] = run_id
    
    cursor = collection.find(query).skip(skip).limit(limit)
    stats_list = await cursor.to_list(length=limit)
    return [EvolutionStats(**stats) for stats in stats_list]

async def update_evolution_stats(stats_id: str, update_data: dict) -> Optional[EvolutionStats]:
    if not ObjectId.is_valid(stats_id):
        return None
    
    result = await collection.update_one(
        {"_id": stats_id},
        {"$set": update_data}
    )
    if result.modified_count > 0:
        return await get_evolution_stats(stats_id)
    return None

async def delete_evolution_stats(stats_id: str) -> bool:
    if not ObjectId.is_valid(stats_id):
        return False
    result = await collection.delete_one({"_id": stats_id})
    return result.deleted_count > 0

async def delete_run_evolution_stats(run_id: str) -> bool:
    if not ObjectId.is_valid(run_id):
        return False
    result = await collection.delete_many({"run_id": ObjectId(run_id)})
    return result.deleted_count > 0 