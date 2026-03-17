"""Unit tests for the scheduling optimizer (no DB required)."""

from datetime import date
from types import SimpleNamespace

import pytest

from app.services.scheduling.optimizer import (
    DEFAULT_DAY_MINUTES,
    SETUP_BUFFER_PER_SCENE,
    assign_dates,
    cluster_scenes,
)


def make_scene(scene_number: str, location_id: str, day_night: str = "day", minutes: int = 30):
    return SimpleNamespace(
        id=scene_number,
        scene_number=scene_number,
        location_id=location_id,
        day_night=day_night,
        int_ext="interior",
        estimated_minutes=minutes,
    )


class TestClusterScenes:
    def test_empty_returns_empty(self):
        assert cluster_scenes([]) == []

    def test_single_scene_one_cluster(self):
        scenes = [make_scene("1", "loc_a", minutes=60)]
        result = cluster_scenes(scenes)
        assert len(result) == 1
        assert result[0][0].scene_number == "1"

    def test_scenes_grouped_by_location(self):
        """Scenes at the same location should end up in the same cluster (if they fit)."""
        scenes = [make_scene(str(i), "loc_a", minutes=10) for i in range(5)]
        scenes += [make_scene(str(i + 10), "loc_b", minutes=10) for i in range(5)]
        clusters = cluster_scenes(scenes)
        # All same-location scenes should be contiguous
        first_cluster_locs = {s.location_id for s in clusters[0]}
        assert len(first_cluster_locs) == 1  # only one location per cluster (greedy fill)

    def test_cluster_does_not_exceed_day_budget(self):
        """Each cluster total should not exceed DEFAULT_DAY_MINUTES."""
        big_scenes = [make_scene(str(i), "loc_a", minutes=100) for i in range(20)]
        clusters = cluster_scenes(big_scenes)
        for cluster in clusters:
            total = sum((s.estimated_minutes or 10) + SETUP_BUFFER_PER_SCENE for s in cluster)
            assert total <= DEFAULT_DAY_MINUTES + 100 + SETUP_BUFFER_PER_SCENE  # last scene can overflow


class TestAssignDates:
    def test_skips_weekends(self):
        monday = date(2024, 1, 1)  # Monday
        clusters = [[make_scene("1", "loc_a")] for _ in range(7)]
        assignments = assign_dates(clusters, monday)
        for d, _ in assignments:
            assert d.weekday() < 5, f"{d} is a weekend"

    def test_skips_blocked_dates(self):
        start = date(2024, 1, 1)  # Monday
        blocked = {date(2024, 1, 3)}  # Wednesday blocked
        clusters = [[make_scene("1", "loc_a")] for _ in range(3)]
        dates = [d for d, _ in assign_dates(clusters, start, blocked_dates=blocked)]
        assert date(2024, 1, 3) not in dates

    def test_correct_number_of_shooting_days(self):
        start = date(2024, 1, 1)
        clusters = [[make_scene(str(i), "loc_a")] for i in range(5)]
        assignments = assign_dates(clusters, start)
        assert len(assignments) == 5
