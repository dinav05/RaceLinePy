
# RaceLinePy

**An open-source Python toolkit for racing line optimization,
track geometry analysis and simracing telemetry.**

RaceLinePy is a personal engineering project exploring the
mathematical and computational methods behind racing line
optimization, vehicle dynamics and motorsport telemetry analysis.

The project is being developed incrementally, with an emphasis
on numerical accuracy, mathematical validation and a modular
Python architecture.

> **Development status:** Early development.
> Track geometry, curvature analysis and periodic Frenet-based
> racing line parametrization are implemented and validated.
> Minimum curvature optimization is the next development milestone.

## Features

### Track Geometry

- Import tracks from the TUM Racetrack Database
- Compute unit tangent and normal vectors
- Reconstruct left and right track boundaries
- Compute segment lengths, cumulative arc length and track length
- Handle closed tracks using periodic indexing

### Curvature Analysis

- Compute signed curvature using periodic central differences
- Visualize curvature profiles along the track
- Display absolute curvature using an interactive color overlay
- Validate numerical curvature against analytical solutions
- Verify second-order convergence on circular test tracks

### Racing Line Representation

- Represent racing lines using lateral Frenet offsets
- Transform Frenet coordinates into Cartesian coordinates
- Distribute control points uniformly along the reference arc length
- Reduce optimization dimensionality through control point parametrization
- Generate smooth offset fields using periodic cubic spline interpolation
- Validate discrete lateral track constraints with configurable safety margins
- Validate transformations and interpolation against analytical reference geometry

### Visualization

- Interactive track viewer
- Track boundaries and driving surface
- Toggleable curvature color map
- Signed curvature profile
- Racing line overlay
- Toggleable control point visualization
- Independent visibility controls for trajectory overlays
- Consistent dark-mode visualization theme

### Racing Line and Interpolation Validation

The Frenet transformation and periodic spline interpolation
have been validated using synthetic circular tracks and
analytical reference functions.

| Metric | Result |
|---|---:|
| Reference track points | 1000 |
| Control points | 20 |
| Reference function | Periodic sine wave |
| Offset amplitude | 3 m |
| Maximum interpolation error | 7.703376e-05 m |
| Maximum interpolation error | 0.077 mm |
| Racing line tests | 11/11 passed |

The validation suite covers:

- Zero-offset identity transformation
- Left and right boundary reconstruction
- Analytical radius validation
- Zero and constant offset interpolation
- Control point reproduction
- Periodic interpolation accuracy
- Lateral constraint validation
- Safety margin validation
- Local constraint violation detection

## Project Structure

```text
RaceLinePy/
├── data/
│   └── tracks/
├── racelinepy/
│   ├── __init__.py
│   ├── track.py
│   ├── racing_line.py
│   └── visualization.py
├── tests/
│   ├── __init__.py
│   ├── test_geometry.py
│   └── test_racing_line.py
├── .gitignore
├── LICENSE
├── main.py
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/dinav05/RaceLinePy.git
cd RaceLinePy
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

The current visualization implementation uses the TkAgg
Matplotlib backend. Tkinter must be available on the system.

## Track Data

RaceLinePy currently uses track data from the
[TUM Racetrack Database](https://github.com/TUMFTM/racetrack-database).

Download the desired track CSV files and place them in:

```text
data/tracks/
```

The default example uses `Spa.csv`.

## Usage

Run the example application:

```bash
python main.py
```

### Track Analysis

```python
from racelinepy.track import Track

track = Track.from_csv("data/tracks/Spa.csv")

length = track.compute_track_length()
curvature = track.compute_curvature()
left, right = track.compute_boundaries()

print(f"Track length: {length:.2f} m")
```


### Racing Line Parametrization

Generate a smooth, periodic racing line using a reduced number
of independent control point offsets.

```python
import numpy as np

from racelinepy.track import Track
from racelinepy.racing_line import RacingLineParametrization
from racelinepy.visualization import plot_track

import matplotlib.pyplot as plt

track = Track.from_csv("data/tracks/Spa.csv")

n_control_points = 100

parametrization = RacingLineParametrization(
    track, n_control_points
)

control_offsets = 3.0 * np.sin(
    np.linspace(
        0, 20 * np.pi,
        n_control_points,
        endpoint=False
    )
)

racing_line = parametrization.create_racing_line(control_offsets)

print(racing_line.is_feasible(margin=0.5))

plot_track(
    track,
    racing_line,
    parametrization,
    control_offsets
)

plt.show()
```

This example generates an artificial periodic trajectory for
visualization and validation purposes.

The lateral constraints are currently evaluated at the discrete
reference track points. Continuous feasibility between sampling
points is not guaranteed.

The trajectory is not yet optimized for curvature or lap time.

## Testing

Run the geometry and racing line validation tests:

```bash
python -m tests.test_geometry
python -m tests.test_racing_line
```

## Roadmap

### Phase 1 — Minimum Curvature Racing Line

- [x] M1 — Track Loader
- [x] M2 — Track Geometry
- [x] M3 — Curvature Analysis
- [x] M4 — Racing Line Parametrization
  - [x] Lateral Frenet offset transformation
  - [x] Control point selection
  - [x] Periodic interpolation
  - [x] Track constraint validation
  - [x] Racing line visualization
- [ ] M5 — Minimum Curvature Optimization
- [ ] M6 — Optimization Validation and Benchmarking

### Phase 2 — Vehicle Dynamics & Lap Time

- [ ] M7 — Vehicle Model
- [ ] M8 — Velocity Profile
- [ ] M9 — Lap Time Estimation
- [ ] M10 — Minimum Lap Time Optimization

### Phase 3 — Telemetry Analysis

- [ ] M11 — Simracing Telemetry Import
- [ ] M12 — Track Coordinate Alignment
- [ ] M13 — Driving and Performance Analysis
- [ ] M14 — Live Telemetry (optional)

## Technologies

- Python
- NumPy
- SciPy
- Matplotlib

## Acknowledgements

Track data is provided by the
[TUM Racetrack Database](https://github.com/TUMFTM/racetrack-database),
developed by the Institute of Automotive Technology at the
Technical University of Munich.

## Disclaimer

RaceLinePy is an experimental engineering and educational
project intended for numerical research and simracing analysis.
It is not intended for safety-critical vehicle control.

## License

RaceLinePy is licensed under the [MIT License](LICENSE).

Third-party track datasets are subject to their respective licenses.
