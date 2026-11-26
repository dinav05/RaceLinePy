from racelinepy.track import Track
from racelinepy.visualization import plot_track, plot_curvature

import matplotlib.pyplot as plt


def main() -> None:
    spa = Track.from_csv("data/tracks/Spa.csv")

    plot_track(spa)
    plot_curvature(spa)

    plt.show()


if __name__ == "__main__":
    main()