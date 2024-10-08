"""
Lists of bookings for rooms.
"""

__all__ = ["router"]


from fastapi import APIRouter

from src.config_schema import Scene
from src.modules.scenes.repository import scene_repository

router = APIRouter(tags=["Scenes"])


@router.get("/scenes/")
def scenes() -> list[Scene]:
    return scene_repository.get_all()
