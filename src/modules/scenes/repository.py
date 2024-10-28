from re import escape, search

from rapidfuzz import fuzz, utils

from src.api.logging_ import logger
from src.config import settings
from src.config_schema import Area, Scene
from src.modules.scenes.schemas import SearchResult


def prepare_for_search(area: Area) -> str | None:
    fields = [area.title, area.description]
    filtered_fields = [field for field in fields if field is not None]

    if not filtered_fields:
        return None

    return " ".join(filtered_fields)


# noinspection PyMethodMayBeStatic
class SceneRepository:
    def get_all(self) -> list[Scene]:
        return settings.scenes

    def search(self, query: str):
        all_scenes = scene_repository.get_all()
        result = []

        for scene in all_scenes:
            logger.debug(scene.areas)

            for index, area in enumerate(scene.areas):
                if area.title and search(rf"\b{escape(query.lower().strip())}", area.title.lower().strip()):
                    result.append(SearchResult(scene_id=scene.scene_id, area_index=index, area=area))
                    if (
                        area.title == "Garage"
                        and area.svg_polygon_id == "garage-0"
                        or area.title == "Reading Hall"
                        and area.svg_polygon_id == "reading-hall-1"
                        or area.title == "Canteen"
                        and area.svg_polygon_id == "canteen"
                        or area.title == "105"
                        and area.svg_polygon_id == "105"
                    ):
                        return [SearchResult(scene_id=scene.scene_id, area_index=index, area=area)]

        if result:
            return result

        for scene in all_scenes:
            logger.debug(scene.areas)
            concatenated_fields = [prepare_for_search(area) for area in scene.areas]

            if not concatenated_fields:
                continue

            matches = [fuzz.token_ratio(query, doc, processor=utils.default_process) for doc in concatenated_fields]
            logger.debug(matches)

            for index, score in enumerate(matches):
                if score >= 60:
                    print(scene.areas[index].title)
                    result.append(SearchResult(scene_id=scene.scene_id, area_index=index, area=scene.areas[index]))

        return result


scene_repository: SceneRepository = SceneRepository()
