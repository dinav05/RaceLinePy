import numpy as np
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

from racelinepy.track import Track


def plot_track(track: Track) -> None:
    """Visualize the track centerline, boundaries and driving surface.

    Args:
        track: Racetrack instance containing the track geometry.
    """

    # Retrieve track geometry.
    centerline = track.centerline
    left, right = track.compute_boundaries()

    # Close the curves for visualization.
    centerline = np.vstack((centerline, centerline[0]))
    left = np.vstack((left, left[0]))
    right = np.vstack((right, right[0]))

    # Construct quadrilateral segments covering the driving surface.
    segments = np.stack(
        (left[:-1], left[1:], right[1:], right[:-1]),
        axis=1
    )

    # Initialize figure and color scheme.
    fig, ax = plt.subplots(figsize=(10, 10))

    fig.patch.set_facecolor("#10151C")
    ax.set_facecolor("#10151C")

    # Draw the track surface.
    surface = PolyCollection(
        segments,
        facecolor="#343B45",
        edgecolor="none",
        antialiased=False,
        zorder=1
    )
    ax.add_collection(surface)

    # Draw track boundaries.
    ax.plot(
        left[:, 0], left[:, 1],
        color="#E2E8F0",
        linewidth=0.8,
        label="Track boundaries",
        zorder=2
    )

    ax.plot(
        right[:, 0], right[:, 1],
        color="#E2E8F0",
        linewidth=0.8,
        zorder=2
    )

    # Draw the reference centerline.
    ax.plot(
        centerline[:, 0], centerline[:, 1],
        color="#64748B",
        linestyle="--",
        linewidth=0.8,
        label="Centerline",
        zorder=3
    )

    # Configure title and axes.
    ax.set_title(
        f"RaceLinePy | {track.name}",
        color="#F1F5F9",
        fontsize=18,
        fontweight="bold",
        pad=20
    )

    ax.set_xlabel("X [m]", color="#94A3B8")
    ax.set_ylabel("Y [m]", color="#94A3B8")
    ax.tick_params(colors="#94A3B8")
    ax.set_aspect("equal")
    ax.margins(0.05)

    # Subtle background grid.
    ax.grid(color="#FFFFFF", alpha=0.05)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color("#343B45")

    # Configure legend.
    ax.legend(
        facecolor="#10151C",
        edgecolor="#343B45",
        labelcolor="#E2E8F0",
        loc="upper right"
    )

    fig.tight_layout()
    plt.show()
