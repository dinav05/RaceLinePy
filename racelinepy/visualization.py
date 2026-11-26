
import numpy as np
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.widgets import CheckButtons

from racelinepy.track import Track


# RaceLinePy visualization color scheme.
BACKGROUND = "#10151C"
SURFACE = "#343B45"
BOUNDARY = "#E2E8F0"
CENTERLINE = "#64748B"
TEXT = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
ACCENT = "#22C55E"


def _style_axes(fig, ax, title: str, xlabel: str, ylabel: str) -> None:
    """Apply the shared RaceLinePy visualization theme."""

    fig.patch.set_facecolor(BACKGROUND)
    ax.set_facecolor(BACKGROUND)

    ax.set_title(
        title,
        color=TEXT,
        fontsize=18,
        fontweight="bold",
        pad=20
    )

    ax.set_xlabel(xlabel, color=TEXT_SECONDARY)
    ax.set_ylabel(ylabel, color=TEXT_SECONDARY)
    ax.tick_params(colors=TEXT_SECONDARY)

    ax.grid(color="#FFFFFF", alpha=0.05)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color(SURFACE)


def plot_track(track: Track) -> None:
    """Visualize track geometry with an interactive curvature overlay.

    Displays the track boundaries and driving surface. A checkbox
    allows switching between the reference centerline and the
    absolute curvature map without changing the current view.

    Args:
        track: Racetrack instance containing the track geometry.
    """

    # Retrieve track geometry and absolute curvature.
    centerline = track.centerline
    left, right = track.compute_boundaries()
    curvature = np.abs(track.compute_curvature())

    # Construct periodic centerline segments.
    next_points = np.roll(centerline, shift=-1, axis=0)
    line_segments = np.stack((centerline, next_points), axis=1)

    # Assign the average curvature magnitude to each segment.
    segment_curvature = (
        curvature + np.roll(curvature, shift=-1)
    ) / 2.0

    # Construct quadrilateral segments covering the driving surface.
    surface_segments = np.stack(
        (
            left,
            np.roll(left, shift=-1, axis=0),
            np.roll(right, shift=-1, axis=0),
            right
        ),
        axis=1
    )

    # Close the curves for visualization.
    centerline = np.vstack((centerline, centerline[0]))
    left = np.vstack((left, left[0]))
    right = np.vstack((right, right[0]))

    # Reserve space for the colorbar and interactive controls.
    fig, ax = plt.subplots(figsize=(7, 8))

    fig.subplots_adjust(
        left=0.12,
        right=0.85,
        bottom=0.14,
        top=0.91
    )

    _style_axes(
        fig, ax,
        title=f"RaceLinePy | {track.name}",
        xlabel="X [m]",
        ylabel="Y [m]"
    )

    # Draw the track surface.
    surface = PolyCollection(
        surface_segments,
        facecolor=SURFACE,
        edgecolor="none",
        antialiased=False,
        zorder=1
    )

    ax.add_collection(surface)

    # Draw track boundaries.
    ax.plot(
        left[:, 0], left[:, 1],
        color=BOUNDARY,
        linewidth=0.8,
        zorder=3
    )

    ax.plot(
        right[:, 0], right[:, 1],
        color=BOUNDARY,
        linewidth=0.8,
        zorder=3
    )

    # Draw the default reference centerline.
    centerline_plot, = ax.plot(
        centerline[:, 0], centerline[:, 1],
        color=CENTERLINE,
        linestyle="--",
        linewidth=0.8,
        zorder=2
    )

    # Define the curvature color scale.
    cmap = LinearSegmentedColormap.from_list(
        "raceline_curvature",
        ["#22C55E", "#EAB308", "#F97316", "#EF4444"]
    )

    norm = Normalize(
        vmin=0.0,
        vmax=max(float(np.max(curvature)), 1e-12)
    )

    # Create the curvature overlay, initially hidden.
    curvature_line = LineCollection(
        line_segments,
        cmap=cmap,
        norm=norm,
        linewidth=2.0,
        capstyle="round",
        zorder=2
    )

    curvature_line.set_array(segment_curvature)
    curvature_line.set_visible(False)

    ax.add_collection(curvature_line)

    # Use a dedicated colorbar axis to prevent layout changes.
    colorbar_ax = fig.add_axes([0.86, 0.22, 0.025, 0.60])

    cbar = fig.colorbar(
        curvature_line,
        cax=colorbar_ax
    )

    cbar.set_label(
        "Absolute curvature [1/m]",
        color=TEXT_SECONDARY,
        labelpad=12
    )

    cbar.ax.tick_params(colors=TEXT_SECONDARY)
    cbar.outline.set_edgecolor(SURFACE)
    cbar.ax.set_visible(False)

    # Configure track proportions and initial view.
    ax.autoscale()
    ax.set_aspect("equal")
    ax.margins(0.05)

    # Create the interactive display controls.
    checkbox_ax = fig.add_axes([0.12, 0.025, 0.55, 0.065])
    checkbox_ax.set_facecolor(BACKGROUND)

    for spine in checkbox_ax.spines.values():
        spine.set_visible(False)

    checkbox = CheckButtons(
        checkbox_ax,
        ["Show curvature"],
        [False],
        label_props={
            "color": [TEXT],
            "fontsize": [12]
        },
        frame_props={
            "edgecolor": [TEXT_SECONDARY],
            "facecolor": [SURFACE],
            "sizes": [150]
        },
        check_props={
            "facecolor": [ACCENT],
            "sizes": [150]
        }
    )

    for label in checkbox.labels:
        label.set_color(TEXT)

    # Switch between the centerline and curvature overlay.
    def toggle_curvature(label: str) -> None:
        visible = checkbox.get_status()[0]

        centerline_plot.set_visible(not visible)
        curvature_line.set_visible(visible)
        cbar.ax.set_visible(visible)

        fig.canvas.draw_idle()

    checkbox.on_clicked(toggle_curvature)

    # Keep the widget alive after this function returns.
    fig._raceline_widgets = [checkbox]


def plot_curvature(track: Track) -> None:
    """Visualize the signed curvature along the track centerline.

    Args:
        track: Racetrack instance containing the track geometry.
    """

    # Compute arc length and signed curvature.
    arc_length = track.compute_arc_length()
    curvature = track.compute_curvature()

    # Convert arc length to kilometers.
    arc_length_km = arc_length / 1000.0

    fig, ax = plt.subplots(figsize=(10, 5))

    _style_axes(
        fig, ax,
        title=f"RaceLinePy | Curvature Profile | {track.name}",
        xlabel="Arc length [km]",
        ylabel="Curvature [1/m]"
    )

    # Plot the signed curvature profile.
    ax.plot(
        arc_length_km,
        curvature,
        color=ACCENT,
        linewidth=1.6,
        label="Signed curvature",
        zorder=3
    )

    # Add the zero-curvature reference line.
    ax.axhline(
        y=0.0,
        color=CENTERLINE,
        linestyle="--",
        linewidth=0.9,
        label="Zero curvature",
        zorder=2
    )

    ax.margins(x=0.01)

    ax.legend(
        facecolor=BACKGROUND,
        edgecolor=SURFACE,
        labelcolor=BOUNDARY,
        loc="upper right"
    )

    fig.tight_layout()
