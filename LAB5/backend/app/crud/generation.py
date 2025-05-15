from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings
from app.models.generation import Generation, GenerationCreate

settings = get_settings()
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]
collection = db.generations

async def create_generation(generation: GenerationCreate) -> Generation:
    generation_dict = generation.model_dump()
    result = await collection.insert_one(generation_dict)
    created_generation = await get_generation(str(result.inserted_id))
    return created_generation

async def get_generation(generation_id: str) -> Optional[Generation]:
    if not ObjectId.is_valid(generation_id):
        return None
    generation = await collection.find_one({"_id": ObjectId(generation_id)})
    return Generation(**generation) if generation else None

async def get_generations(
    run_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Generation]:
    if not ObjectId.is_valid(run_id):
        return []
    
    cursor = collection.find(
        {"run_id": ObjectId(run_id)}
    ).sort("generation_number", -1).skip(skip).limit(limit)
    
    generations = await cursor.to_list(length=limit)
    return [Generation(**gen) for gen in generations]

async def get_latest_generation(run_id: str) -> Optional[Generation]:
    if not ObjectId.is_valid(run_id):
        return None
    
    generation = await collection.find_one(
        {"run_id": ObjectId(run_id)},
        sort=[("generation_number", -1)]
    )
    return Generation(**generation) if generation else None

async def update_generation(generation_id: str, update_data: dict) -> Optional[Generation]:
    if not ObjectId.is_valid(generation_id):
        return None
    
    result = await collection.update_one(
        {"_id": ObjectId(generation_id)},
        {"$set": update_data}
    )
    if result.modified_count > 0:
        return await get_generation(generation_id)
    return None

async def delete_generation(generation_id: str) -> bool:
    if not ObjectId.is_valid(generation_id):
        return False
    result = await collection.delete_one({"_id": ObjectId(generation_id)})
    return result.deleted_count > 0

async def delete_run_generations(run_id: str) -> bool:
    if not ObjectId.is_valid(run_id):
        return False
    result = await collection.delete_many({"run_id": ObjectId(run_id)})
    return result.deleted_count > 0 