
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
> Track geometry, curvature analysis and Frenet-based racing
> line representation are implemented. Optimization is in progress.

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
- Validate transformations against analytical reference geometry

### Visualization

- Interactive track viewer
- Track boundaries and driving surface
- Toggleable curvature color map
- Signed curvature profile
- Consistent dark-mode visualization theme

## Numerical Validation

The numerical curvature algorithm has been validated against
a uniformly sampled circular track with a radius of 100 m.

| Metric | Result |
|---|---:|
| Number of points | 1000 |
| Analytical curvature | 0.0100000000 m⁻¹ |
| Numerical curvature | 0.0099999507 m⁻¹ |
| Maximum absolute error | 4.935 × 10⁻⁸ m⁻¹ |
| Relative error | 0.000493% |

A convergence study confirmed second-order convergence on
the circular test track.

| Number of points | Maximum absolute error | Error ratio |
|---:|---:|---:|
| 20 | 1.231166e-04 | — |
| 40 | 3.082666e-05 | 3.993835 |
| 80 | 7.709638e-06 | 3.998458 |
| 160 | 1.927595e-06 | 3.999614 |
| 320 | 4.819104e-07 | 3.999904 |
| 640 | 1.204783e-07 | 3.999976 |
| 1280 | 3.011966e-08 | 3.999990 |

The reconstructed Spa-Francorchamps centerline has a computed
length of 7000.05 m, compared to the official circuit length
of 7004 m.

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

### Racing Line Representation

```python
import numpy as np
from racelinepy.racing_line import RacingLine

offsets = np.zeros(len(track.centerline))
racing_line = RacingLine(track, offsets)

coordinates = racing_line.to_cartesian()
```

Positive lateral offsets point towards the left track boundary,
while negative offsets point towards the right boundary.

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
- [ ] M4 — Racing Line Parametrization
  - [x] Lateral Frenet offset transformation
  - [ ] Control point selection
  - [ ] Periodic interpolation
  - [ ] Track constraint validation
  - [ ] Racing line visualization
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
