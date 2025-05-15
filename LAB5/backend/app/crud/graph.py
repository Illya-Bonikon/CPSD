from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings
from app.models.graph import Graph, GraphCreate, GraphUpdate

settings = get_settings()
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]
collection = db.graphs

async def create_graph(graph: GraphCreate) -> Graph:
    """Створення нового графа"""
    now = datetime.utcnow()
    graph_dict = graph.model_dump()
    graph_dict.update({
        "created_at": now,
        "updated_at": now
    })
    
    result = await collection.insert_one(graph_dict)
    created_graph = await collection.find_one({"_id": result.inserted_id})
    return Graph(
        id=str(created_graph["_id"]),
        **{k: v for k, v in created_graph.items() if k != "_id"}
    )

async def get_graphs(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None
) -> List[Graph]:
    """Отримання списку графів з фільтрацією та пагінацією"""
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    
    cursor = collection.find(query).skip(skip).limit(limit)
    graphs = await cursor.to_list(length=limit)
    
    return [
        Graph(
            id=str(graph["_id"]),
            **{k: v for k, v in graph.items() if k != "_id"}
        )
        for graph in graphs
    ]

async def get_graph(graph_id: str) -> Optional[Graph]:
    """Отримання графа за ID"""
    from bson.objectid import ObjectId
    try:
        graph = await collection.find_one({"_id": ObjectId(graph_id)})
        if graph:
            return Graph(
                id=str(graph["_id"]),
                **{k: v for k, v in graph.items() if k != "_id"}
            )
    except:
        return None
    return None

async def update_graph(graph_id: str, graph: GraphUpdate) -> Optional[Graph]:
    """Оновлення графа"""
    from bson.objectid import ObjectId
    try:
        update_data = graph.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"_id": ObjectId(graph_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            updated_graph = await collection.find_one({"_id": ObjectId(graph_id)})
            return Graph(
                id=str(updated_graph["_id"]),
                **{k: v for k, v in updated_graph.items() if k != "_id"}
            )
    except:
        return None
    return None

async def delete_graph(graph_id: str) -> bool:
    """Видалення графа"""
    from bson.objectid import ObjectId
    try:
        result = await collection.delete_one({"_id": ObjectId(graph_id)})
        return result.deleted_count > 0
    except:
        return False

async def get_graph_by_name(name: str) -> Optional[Graph]:
    graph = await collection.find_one({"name": name})
    return Graph(**graph) if graph else None 