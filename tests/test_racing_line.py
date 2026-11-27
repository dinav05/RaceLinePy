
import numpy as np

from racelinepy.racing_line import RacingLine, RacingLineParametrization
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

def test_zero_control_offsets() -> None:
    """Verify that zero control offsets produce a zero offset field."""

    track = create_circle_track(100.0, 1000)
    parametrization = RacingLineParametrization(track, 20)

    control_offsets = np.zeros(20)
    offsets = parametrization.interpolate_offsets(control_offsets)

    assert offsets.shape == (1000,)
    assert np.allclose(offsets, 0.0)


def test_constant_control_offsets() -> None:
    """Verify that interpolation preserves constant lateral offsets."""

    track = create_circle_track(100.0, 1000)
    parametrization = RacingLineParametrization(track, 20)

    control_offsets = np.full(20, 3.0)
    offsets = parametrization.interpolate_offsets(control_offsets)

    assert np.allclose(offsets, 3.0)


def test_control_point_reproduction() -> None:
    """Verify that the interpolated spline passes through its control points."""

    n_points = 1000
    n_control_points = 20

    track = create_circle_track(100.0, n_points)
    parametrization = RacingLineParametrization(track, n_control_points)

    # Generate nonconstant periodic control offsets.
    angles = np.linspace(
        0, 2*np.pi, n_control_points, endpoint=False
    )
    control_offsets = 3.0 * np.sin(angles)

    offsets = parametrization.interpolate_offsets(control_offsets)

    # Every 50th centerline point coincides with a control point.
    stride = n_points // n_control_points

    assert np.allclose(offsets[::stride], control_offsets)


def test_periodic_interpolation() -> None:
    """Validate periodic interpolation against an analytical sine function."""

    track = create_circle_track(100.0, 1000)
    parametrization = RacingLineParametrization(track, 20)

    track_length = track.compute_track_length()

    # Sample an analytical periodic function at the control points.
    control_offsets = 3.0 * np.sin(
        2*np.pi * parametrization.control_s / track_length
    )

    offsets = parametrization.interpolate_offsets(control_offsets)

    # Evaluate the analytical reference at all centerline points.
    reference_offsets = 3.0 * np.sin(
        2*np.pi * track.compute_arc_length() / track_length
    )

    # Quantify the maximum interpolation error.
    error_max_abs = np.max(np.abs(offsets - reference_offsets))

    print(f"Maximum interpolation error: {error_max_abs:.6e} m")

    # Require submillimeter interpolation accuracy.
    assert error_max_abs < 1e-3   

def test_feasibility() -> None:
    """Verify feasibility for offsets inside and outside the track limits."""

    track = create_circle_track(100.0, 1000)

    # Test valid offsets, including both track boundaries.
    for offset in [0.0, 3.0, -3.0, 5.0, -5.0]:
        racing_line = RacingLine(track, np.full(1000, offset))
        assert racing_line.is_feasible()

    # Test offsets exceeding either track boundary.
    for offset in [6.0, -6.0]:
        racing_line = RacingLine(track, np.full(1000, offset))
        assert not racing_line.is_feasible()


def test_feasibility_margin() -> None:
    """Verify that the safety margin reduces the feasible track width."""

    track = create_circle_track(100.0, 1000)

    # Valid offsets with a safety margin of 1 m.
    for offset in [0.0, 4.0, -4.0]:
        racing_line = RacingLine(track, np.full(1000, offset))
        assert racing_line.is_feasible(margin=1.0)

    # Offsets violating the safety margin.
    for offset in [4.5, -4.5]:
        racing_line = RacingLine(track, np.full(1000, offset))
        assert not racing_line.is_feasible(margin=1.0)


def test_local_constraint_violation() -> None:
    """Verify that a single invalid offset makes the racing line infeasible."""

    track = create_circle_track(100.0, 1000)

    # Introduce a single local track boundary violation.
    offsets = np.zeros(1000)
    offsets[500] = 6.0

    racing_line = RacingLine(track, offsets)

    assert not racing_line.is_feasible()     


if __name__ == "__main__":
    test_zero_offsets()
    print("[PASS] Zero offsets")

    test_left_boundary_offsets()
    print("[PASS] Left boundary offsets")

    test_right_boundary_offsets()
    print("[PASS] Right boundary offsets")

    test_constant_offset_radius()
    print("[PASS] Analytical radius validation")

    test_zero_control_offsets()
    print("[PASS] Zero control offsets")

    test_constant_control_offsets()
    print("[PASS] Constant control offsets")

    test_control_point_reproduction()
    print("[PASS] Control point reproduction")

    test_periodic_interpolation()
    print("[PASS] Periodic interpolation")

    test_feasibility()
    print("[PASS] Feasibility")

    test_feasibility_margin()
    print("[PASS] Feasibility with safety margin")

    test_local_constraint_violation()
    print("[PASS] Local constraint violation")

    print("\nAll racing line tests passed.")