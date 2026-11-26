from racelinepy.track import Track
from racelinepy.visualization import plot_track

spa = Track.from_csv("data/tracks/Spa.csv")

plot_track(spa)

