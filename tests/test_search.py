from unittest import TestCase

import pytest

from src.modules.scenes.repository import scene_repository

# [
#   (query, [(scene-id, svg-polygon-id), ...]),
#   ...
# ]
cases = [
    # Exact match (simple case, without postfixes
    ("305", [("university-floor-3", "305")]),
    ("404", [("university-floor-4", "404")]),
    ("3.2", [("university-floor-3", "3.2")]),
    # Postfixes (a, b, c)
    ("504a", [("university-floor-5", "504a")]),
    ("309a", [("university-floor-3", "309a")]),
    ("411", [("university-floor-4", "411"), ("university-floor-4", "411a")]),  # exact match + postfix
    ("309", [("university-floor-3", "309"), ("university-floor-4", "309a")]),  # exact match + postfix
    ("450", [("university-floor-4", "450"), ("university-floor-4", "450a")]),  # exact match + postfix
    ("504", [("university-floor-5", "504a"), ("university-floor-5", "504b"), ("university-floor-5", "504c")]),
    # 105 and 105a case is tricky, we have 105 on Floor 1 and 105a on Floor -1
    ("105", [("university-floor-1", "105")]),
    ("105a", [("university-floor-0", "105a")]),
    #
    ("Canteen", [("university-floor-1", "canteen")]),
    ("Reading Hall", [("university-floor-1", "reading-hall-1")]),
    ("Garage", [("university-floor-0", "garage-0")]),  # Garage should be Floor -1
]


@pytest.mark.parametrize("input_, desired", cases, ids=[x for x, _ in cases])
def test_location_parser(input_: str, desired: list[tuple[str, str]]):
    # desired - list of svg_polygon_id
    results = scene_repository.search(input_)
    _ = TestCase()
    _.maxDiff = None

    to_compare = {(result.scene_id, result.area.svg_polygon_id) for result in results}
    _.assertSetEqual(to_compare, set(desired))
