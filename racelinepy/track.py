import numpy as np
from numpy.typing import NDArray
from pathlib import Path

class Track:
    """Represents a closed racetrack using a reference centerline
    and lateral track widths.

    Attributes:
        name: Name of the racetrack.
        centerline: Reference coordinates in meters, shape (N, 2).
        width_left: Distance to the left boundary in meters, shape (N,).
        width_right: Distance to the right boundary in meters, shape (N,).
    """
    def __init__(self, 
                 name: str, 
                 centerline: NDArray[np.float64], 
                 width_left: NDArray[np.float64], 
                 width_right: NDArray[np.float64]
                 ):
        
        self.name = name
        self.centerline = centerline
        self.width_left = width_left
        self.width_right = width_right


    @classmethod
    def from_csv(cls, file: str, name: str | None = None) -> "Track":
        """Load a racetrack from a TUM Racetrack Database CSV file.

        Args:
            file: Path to the CSV file.
            name: Optional track name. Defaults to the filename
                without its extension.

        Returns:
            Track: Racetrack instance containing the loaded geometry.
        """

        if name is None:
            name = Path(file).stem

        track_data = np.loadtxt(fname=file, dtype=np.float64, delimiter=",", comments="#")

        # TUM CSV column order: x, y, right width, left width.
        centerline = track_data[:,:2]
        width_right = track_data[:, 2]
        width_left = track_data[:, 3]

        return cls(name, centerline, width_left, width_right)


    def compute_tangents(self) -> NDArray[np.float64]:
        """Compute unit tangent vectors along the track centerline.

        Uses central differences with periodic indexing to approximate
        the local track direction at each point.

        Returns:
            NDArray[np.float64]: Unit tangent vectors of shape (N, 2),
                pointing in the direction of increasing track index.
        """

        # Approximate tangent directions using periodic central differences.
        diff_vectors = np.roll(self.centerline, shift=-1, axis=0) - np.roll(self.centerline, shift=1, axis=0)
        # Preserve the second dimension to enable row-wise broadcasting.
        norms = np.linalg.norm(diff_vectors, axis=1, keepdims=True)

        normed_vectors = diff_vectors/norms

        return normed_vectors

    def compute_normals(self) -> NDArray[np.float64]:
        """Compute left-pointing unit normal vectors along the track.

        Rotates the tangent vectors counterclockwise by 90 degrees.
        Positive normal directions point towards the left track boundary.

        Returns:
            NDArray[np.float64]: Unit normal vectors of shape (N, 2).
        """

        tangents = self.compute_tangents()

        tangents_x = tangents[:, 0]
        tangents_y = tangents[:, 1]

        # Rotate each tangent vector by +90 degrees: (x, y) -> (-y, x).
        normals = np.column_stack([-tangents_y, tangents_x])

        return normals

    def compute_boundaries(self) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute the left and right track boundaries.

        Offsets each centerline point along its unit normal vector
        by the corresponding lateral track width.

        Returns:
            tuple[NDArray[np.float64], NDArray[np.float64]]:
                Left and right boundary coordinates in meters,
                each of shape (N, 2).
        """

        # Reshape track widths to (N, 1) for row-wise broadcasting.
        width_l = self.width_left[:, None]
        width_r = self.width_right[:, None]

        # Offset the centerline along the left-pointing unit normals.
        normals = self.compute_normals()

        boundary_left = self.centerline + normals * width_l
        boundary_right = self.centerline - normals * width_r

        return boundary_left, boundary_right


    def compute_segment_lengths(self) -> NDArray[np.float64]:
        """Compute the distances between consecutive centerline points.

        Includes the closing segment from the last point to the first
        point using periodic indexing.

        Returns:
            NDArray[np.float64]: Segment lengths in meters, shape (N,).
        """

        # Compute forward displacement vectors with periodic indexing.
        forward_vectors = np.roll(self.centerline, shift=-1, axis=0) - self.centerline

        segment_lengths = np.linalg.norm(forward_vectors, axis=1)

        return segment_lengths

    def compute_arc_length(self) -> NDArray[np.float64]:

        """Compute the cumulative arc length along the centerline.

        The first point defines the origin (s = 0). The closing segment
        is excluded to maintain one arc length value per centerline point.

        Returns:
            NDArray[np.float64]: Cumulative distances in meters, shape (N,).
        """

        # Exclude the closing segment and prepend the origin at s = 0.
        return np.insert(
            np.cumsum(self.compute_segment_lengths()[:-1]),
            0,
            0.0
        )

    def compute_track_length(self) -> float:
        """Compute the total length of the closed track centerline.

        Includes all segments, including the closing segment from
        the last point to the first point.

        Returns:
            float: Total track length in meters.
        """
        
        return float(np.sum(self.compute_segment_lengths()))


    def compute_curvature(self) -> NDArray[np.float64]:
        """Compute the signed curvature along the track centerline.

        Approximates the derivative of the unit tangent vectors with
        respect to arc length using periodic central differences.
        Projects the resulting derivative onto the unit normal vectors.

        Positive curvature indicates a left turn, while negative
        curvature indicates a right turn.

        Returns:
            NDArray[np.float64]: Signed curvature in inverse meters
                (1/m), shape (N,).
        """

        tangents = self.compute_tangents()


        # Compute the change in tangent direction using periodic central differences.
        delta_tangents = np.roll(tangents, shift=-1, axis=0) - np.roll(tangents, shift=1, axis=0)


        segment_lengths = self.compute_segment_lengths()

        # Sum adjacent segment lengths to obtain the central difference interval.
        ds = (np.roll(segment_lengths, shift=1) + segment_lengths)[:, None]

        # Approximate the derivative of the unit tangents with respect to arc length.
        dtangent_ds = delta_tangents / ds


        normals = self.compute_normals()

        # Project the tangent derivative onto the left-pointing unit normals.
        curvature = np.sum(dtangent_ds * normals, axis=1)

        return curvature