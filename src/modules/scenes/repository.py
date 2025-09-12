from re import escape, search

from rapidfuzz import fuzz, utils

from src.api.logging_ import logger
from src.config import scenes
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
        return scenes

    def search(self, query: str):
        all_scenes = scene_repository.get_all()
        result = []

        for scene in all_scenes:
            logger.debug(scene.areas)

            for index, area in enumerate(scene.areas):
                for title in filter(None, (area.title, area.ru_title)):
                    query_clean = query.lower().strip()
                    title_clean = title.lower().strip()

                    # Handle [SC] prefix searches specially - only search in sport-complex scene
                    if query_clean.startswith("[sc]") or query_clean.startswith("[ск]"):
                        if scene.scene_id == "sport-complex":
                            # Check if the rest of the query matches in sport complex
                            query_without_prefix = query_clean.replace("[sc]", "").replace("[ск]", "").strip()
                            if query_without_prefix in title_clean or search(
                                rf"{escape(query_without_prefix)}", title_clean
                            ):
                                if area.prioritized:
                                    return [SearchResult(scene_id=scene.scene_id, area_index=index, area=area)]
                                result.append(SearchResult(scene_id=scene.scene_id, area_index=index, area=area))
                    # Handle Music room 020 special case
                    elif "music room 020" in query_clean or "музыкальная комната 020" in query_clean:
                        if "music room" in title_clean or "музыкальная комната" in title_clean:
                            if area.prioritized:
                                return [SearchResult(scene_id=scene.scene_id, area_index=index, area=area)]
                            result.append(SearchResult(scene_id=scene.scene_id, area_index=index, area=area))
                    else:
                        # Regular search with word boundaries
                        if search(rf"\b{escape(query_clean)}", title_clean):
                            if area.prioritized:
                                return [SearchResult(scene_id=scene.scene_id, area_index=index, area=area)]
                            result.append(SearchResult(scene_id=scene.scene_id, area_index=index, area=area))

        if result:
            return result

        people_results: list[tuple[float, Scene, int]] = []
        for scene in all_scenes:
            for index, area in enumerate(scene.areas):
                for person in area.people:
                    score = fuzz.partial_ratio(query.lower().strip(), person.lower())
                    people_results.append((score, scene, index))
        if people_results:
            score, scene, index = max(people_results, key=lambda x: x[0])
            if score > 70:
                return [SearchResult(scene_id=scene.scene_id, area_index=index, area=scene.areas[index])]

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
