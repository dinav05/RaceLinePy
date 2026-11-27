import numpy as np

from racelinepy.track import Track
from racelinepy.racing_line import RacingLineParametrization
from racelinepy.visualization import plot_track, plot_curvature

import matplotlib.pyplot as plt


def main() -> None:
    spa = Track.from_csv("data/tracks/Spa.csv")

    n_control_points = 100
    parametrization = RacingLineParametrization(
        spa, n_control_points
    )

    # Generate an artificial periodic racing line.
    control_offsets = 3.0 * np.sin(
        np.linspace(
            0, 2 * np.pi * 10,
            n_control_points,
            endpoint=False
        )
    )

    racing_line = parametrization.create_racing_line(
        control_offsets
    )

    print(f"Racing line feasible: {racing_line.is_feasible()}")

    plot_track(
        spa,
        racing_line,
        parametrization,
        control_offsets
    )

    plot_curvature(spa)

    plt.show()


if __name__ == "__main__":
    main()