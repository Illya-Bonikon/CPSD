from fastapi import APIRouter
from .endpoints import graphs, algorithm, statistics

api_router = APIRouter()

api_router.include_router(
    graphs.router,
    prefix="/graphs",
    tags=["graphs"]
)

api_router.include_router(
    algorithm.router,
    prefix="/algorithm",
    tags=["algorithm"]
)

api_router.include_router(
    statistics.router,
    prefix="/statistics",
    tags=["statistics"]
) 