from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import get_settings

settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongodb(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        
        # Створюємо індекси
        await self.create_indexes()

    async def close_mongodb_connection(self):
        if self.client:
            self.client.close()

    async def create_indexes(self):
        # Індекси для графів
        await self.db.graphs.create_index("name", unique=True)
        await self.db.graphs.create_index("vertices")
        await self.db.graphs.create_index("is_complete")

        # Індекси для запусків алгоритму
        await self.db.algorithm_runs.create_index("graph_id")
        await self.db.algorithm_runs.create_index("status")
        await self.db.algorithm_runs.create_index("start_time")
        await self.db.algorithm_runs.create_index([("graph_id", 1), ("status", 1)])

        # Індекси для поколінь
        await self.db.generations.create_index("run_id")
        await self.db.generations.create_index([("run_id", 1), ("generation_number", 1)], unique=True)

        # Індекси для статистики еволюції
        await self.db.evolution_stats.create_index("run_id", unique=True)

mongodb = MongoDB() 