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