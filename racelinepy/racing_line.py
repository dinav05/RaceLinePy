import numpy as np
from numpy.typing import NDArray
from racelinepy.track import Track

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