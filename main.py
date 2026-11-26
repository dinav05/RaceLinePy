from racelinepy.track import Track
from racelinepy.visualization import plot_track
import numpy as np

spa = Track.from_csv("data/tracks/Spa.csv")

s = spa.compute_arc_length()

print(s[:5])
print(s[-5:])
print(s.shape)
print(spa.compute_track_length())