from src.config import settings
from src.config_schema import Scene


# noinspection PyMethodMayBeStatic
class SceneRepository:
    def get_all(self) -> list[Scene]:
        return settings.scenes


scene_repository: SceneRepository = SceneRepository()
