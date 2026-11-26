
import numpy as np

from racelinepy.racing_line import RacingLine
from tests.test_geometry import create_circle_track


def test_zero_offsets() -> None:
    """Verify that zero lateral offsets reproduce the centerline."""

    track = create_circle_track(100.0, 1000)

    offsets = np.zeros(1000)
    racing_line = RacingLine(track, offsets)

    coordinates = racing_line.to_cartesian()

    assert np.allclose(coordinates, track.centerline)


def test_left_boundary_offsets() -> None:
    """Verify that maximum positive offsets reproduce the left boundary."""

    track = create_circle_track(100.0, 1000)
    left_boundary, _ = track.compute_boundaries()

    # Positive offsets point towards the left track boundary.
    racing_line = RacingLine(track, track.width_left)

    coordinates = racing_line.to_cartesian()

    assert np.allclose(coordinates, left_boundary)


def test_right_boundary_offsets() -> None:
    """Verify that maximum negative offsets reproduce the right boundary."""

    track = create_circle_track(100.0, 1000)
    _, right_boundary = track.compute_boundaries()

    # Negative offsets point towards the right track boundary.
    racing_line = RacingLine(track, -track.width_right)

    coordinates = racing_line.to_cartesian()

    assert np.allclose(coordinates, right_boundary)


def test_constant_offset_radius() -> None:
    """Validate the Frenet transformation against an analytical circle.

    For a counterclockwise circular track, a positive lateral offset
    reduces the circle radius by the specified offset.
    """

    radius = 100.0
    offset = 3.0
    n_points = 1000

    track = create_circle_track(radius, n_points)
    offsets = np.full(n_points, offset)

    racing_line = RacingLine(track, offsets)
    coordinates = racing_line.to_cartesian()

    # Calculate the distance of each point from the circle origin.
    radii = np.linalg.norm(coordinates, axis=1)

    # Analytical radius after applying the lateral offset.
    expected_radius = radius - offset

    assert np.allclose(radii, expected_radius)


if __name__ == "__main__":
    test_zero_offsets()
    print("[PASS] Zero offsets")

    test_left_boundary_offsets()
    print("[PASS] Left boundary offsets")

    test_right_boundary_offsets()
    print("[PASS] Right boundary offsets")

    test_constant_offset_radius()
    print("[PASS] Analytical radius validation")

    print("\nAll racing line tests passed.")
