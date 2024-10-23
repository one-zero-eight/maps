"""
Lists of bookings for rooms.
"""

__all__ = ["router"]

from fastapi import APIRouter, Query
from pydantic import BaseModel
from rapidfuzz import fuzz, utils

from src.api.logging_ import logger
from src.config_schema import Area, Scene
from src.modules.scenes.repository import scene_repository

router = APIRouter(tags=["Scenes"])


class SearchResult(BaseModel):
    scene_id: str
    matching_area_indexes: list[int]


@router.get("/scenes/")
def scenes() -> list[Scene]:
    return scene_repository.get_all()


def prepare_for_search(area: Area) -> str | None:
    fields = [area.title, area.description]
    filtered_fields = [field for field in fields if field is not None]

    if not filtered_fields:
        return None

    return " ".join(filtered_fields)


@router.get("/scenes/areas/search", response_model=list[SearchResult])
def search_areas(query: str = Query(..., min_length=1)) -> list[SearchResult]:
    all_scenes = scene_repository.get_all()
    result = []
    logger.info(f"Searching areas for {query}")
    for scene in all_scenes:
        logger.info(scene.areas)
        concatenated_fields = [prepare_for_search(area) for area in scene.areas]

        if not concatenated_fields:
            continue

        for index, area in enumerate(scene.areas):
            if area.title and query.lower().strip() == area.title.lower().strip():
                return [SearchResult(scene_id=scene.scene_id, matching_area_indexes=[index])]
        matches = [fuzz.token_ratio(query, doc, processor=utils.default_process) for doc in concatenated_fields]
        logger.info(matches)

        matching_indexes = []
        for index, score in enumerate(matches):
            if score >= 60:
                matching_indexes.append(index)

        if matching_indexes:
            result.append(
                SearchResult(
                    scene_id=scene.scene_id,
                    matching_area_indexes=matching_indexes,
                )
            )

    return result
