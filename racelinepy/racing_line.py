import numpy as np
from numpy.typing import NDArray
from racelinepy.track import Track
from scipy.interpolate import CubicSpline

class RacingLine:
    """Represents a racing line in Frenet coordinates relative to a track.

    Attributes:
        track: Reference track defining the underlying geometry.
        offsets: Lateral offsets in meters, shape (N,).
            Positive values point left, negative values point right.
    """
    def __init__(self, 
                 track: Track, 
                 offsets: NDArray[np.float64]
                 ):

        if offsets.shape != (len(track.centerline),):
            raise ValueError("Expected one lateral offset per centerline point.")
        
        self.track = track
        self.offsets = offsets


    def to_cartesian(self) -> NDArray[np.float64]:
        """Transform lateral Frenet offsets into Cartesian coordinates.

        Displaces each reference centerline point along its corresponding
        unit normal vector by the specified lateral offset.

        Returns:
            NDArray[np.float64]: Cartesian racing line coordinates
                in meters, shape (N, 2).
        """

        normals = self.track.compute_normals()
        centerline = self.track.centerline

        # Transform lateral offsets into Cartesian displacements.
        cartesian_coordinates = centerline + normals * self.offsets[:, None]

        return cartesian_coordinates

    def is_feasible(self, margin: float = 0.0) -> bool:
        """Check whether the racing line satisfies the lateral track limits.

        Evaluates all discrete lateral offsets against the left and right
        track boundaries, accounting for an optional safety margin.

        Args:
            margin: Minimum lateral clearance from the track boundaries
                in meters. Defaults to 0.0.

        Returns:
            bool: True if all discrete racing line points satisfy the
                lateral constraints, False otherwise.

        Raises:
            ValueError: If the safety margin is negative.
        """

        if margin < 0:
            raise ValueError("Margin must be non-negative.")
        
        return (
                np.all(self.offsets <= self.track.width_left - margin) and 
                np.all(self.offsets >= -self.track.width_right + margin)
                )

class RacingLineParametrization:
    """Parametrize racing lines using a reduced set of control points.

    Control points are distributed uniformly along the reference
    track's arc length. Their lateral offsets serve as independent
    decision variables for racing line optimization.

    Attributes:
        track: Reference track defining the underlying geometry.
        control_s: Longitudinal control point positions in meters,
            shape (M,), where M is the number of control points.
    """

    def __init__(self, track: Track, n_control_points: int):

        self.track = track

        # Require at least three independent control points.
        if n_control_points < 3:
            raise ValueError("At least three control points are required.")

        # Distribute control points uniformly along the reference arc length.
        # Exclude the endpoint to avoid duplicating the start/finish point.
        self.control_s = np.linspace(0, 
                                     track.compute_track_length(), 
                                     n_control_points,
                                     endpoint=False
                                     )

        

    def interpolate_offsets(self, 
                            control_offsets: NDArray[np.float64]
                            ) -> NDArray[np.float64]:
        """Interpolate lateral control point offsets along the reference track.

        Uses periodic cubic spline interpolation to generate a smooth
        offset field with continuous first and second derivatives
        across the start/finish transition.

        Args:
            control_offsets: Lateral control point offsets in meters,
                shape (M,).

        Returns:
            NDArray[np.float64]: Interpolated lateral offsets in meters,
                shape (N,), with one offset per centerline point.

        Raises:
            ValueError: If the number or shape of control offsets does
                not match the control point positions.
        """

        # Ensure that each control point has exactly one lateral offset.
        if control_offsets.shape != self.control_s.shape:
            raise ValueError("Expected one lateral offset per control point.")

        # Close the interpolation interval by duplicating the first
        # control offset at the end of the reference track.
        periodic_s = np.append(self.control_s, self.track.compute_track_length())
        periodic_offsets = np.append(control_offsets, control_offsets[0])

        # Construct a cubic spline with periodic boundary conditions.
        spline = CubicSpline(periodic_s, periodic_offsets, bc_type="periodic")

        # Evaluate the spline at the original centerline arc length positions.
        query_s = self.track.compute_arc_length()

        interpolated_offsets = spline(query_s)

        return interpolated_offsets

    def create_racing_line(self, control_offsets: NDArray[np.float64]
                           ) -> RacingLine:
        """Create a racing line from a reduced set of control point offsets.

        Args:
            control_offsets: Lateral control point offsets in meters,
                shape (M,).

        Returns:
            RacingLine: Racing line containing the interpolated lateral
                offsets at all reference centerline points.
        """

        return RacingLine(self.track, 
                          self.interpolate_offsets(control_offsets)
                          )