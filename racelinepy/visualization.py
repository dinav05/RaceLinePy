import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from racelinepy.track import Track

def plot_track(track: Track) -> None:

    track_x = track.centerline[:, 0]
    track_y = track.centerline[:, 1]

    plt.plot(track_x, track_y)
    plt.axis("equal")
    plt.title("Track: " + track.name)
    plt.show()