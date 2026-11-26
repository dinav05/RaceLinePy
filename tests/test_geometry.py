import numpy as np
from racelinepy.track import Track


def create_circle_track(radius: float, n_points: int) -> Track:
    """Generate a synthetic circular track for analytical validation.

    The centerline is sampled uniformly in the counterclockwise
    direction, resulting in positive curvature.

    Args:
        radius: Radius of the circle in meters.
        n_points: Number of discrete centerline points.

    Returns:
        Track: Circular track with constant lateral widths of 5 m.
    """

    # Exclude the endpoint to avoid duplicating the first track point.    
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)

    # Generate Cartesian coordinates from the parametric circle equation.
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)

    centerline = np.column_stack((x, y))

    # Assign constant lateral widths to the synthetic track.
    width_left = np.full(n_points, 5.0)
    width_right = np.full(n_points, 5.0)

    track = Track("TestCircle", centerline, width_left, width_right)

    return track



def test_circle_curvature():
    """Validate numerical curvature against the analytical solution
    of a uniformly sampled circular track.
    """

    radius = 100.0
    n_points = 1000
    track = create_circle_track(radius, n_points)

    curvature = track.compute_curvature()

    # Analytical curvature of a circle: kappa = 1 / R.
    curvature_reference = 1 / radius

    curvature_min = np.min(curvature)
    curvature_max = np.max(curvature)
    curvature_mean = np.mean(curvature)
    curvature_std = np.std(curvature)

    # Quantify the numerical approximation error.
    error_max_abs = np.max(np.abs(curvature - curvature_reference))
    error_rel = error_max_abs / np.abs(curvature_reference)

    print(f"Circle radius:        {radius:.2f} m")
    print(f"Number of points:     {n_points}")
    print(f"Reference curvature:  {curvature_reference:.10f} 1/m")
    print(f"Minimum curvature:    {curvature_min:.10f} 1/m")
    print(f"Maximum curvature:    {curvature_max:.10f} 1/m")
    print(f"Mean curvature:       {curvature_mean:.10f} 1/m")
    print(f"Standard deviation:   {curvature_std:.6e} 1/m")
    print(f"Max. absolute error:  {error_max_abs:.6e} 1/m")
    print(f"Relative error:       {error_rel:.6%}")

    # Verify numerical curvature against the analytical reference.
    assert np.allclose(curvature, curvature_reference, rtol=1e-5, atol=0.0)

def test_curvature_convergence():
    """Validate the convergence order of the numerical curvature method.

    Evaluates the maximum absolute curvature error on circular tracks
    with progressively increasing spatial resolution.

    The central difference approximation is expected to exhibit
    second-order convergence, reducing the error by approximately
    a factor of four when the number of points is doubled.
    """

    radius = 100.0
    resolutions = [20, 40, 80, 160, 320, 640, 1280]

    # Generate circular tracks with progressively finer discretization.
    tracks = [create_circle_track(radius, n_points) for n_points in resolutions]

    curvatures = [track.compute_curvature() for track in tracks]

    curvature_reference = 1 / radius

    # Compute the maximum absolute curvature error for each resolution.
    errors = np.array([
        np.max(np.abs(curvature - curvature_reference))
        for curvature in curvatures
    ])

    # Compare successive errors to verify second-order convergence.
    ratios = errors[:-1] / errors[1:]

    print(f"{'Points':>8} {'Max. abs. error':>20} {'Error ratio':>15}")
    print("-" * 45)

    for i, n_points in enumerate(resolutions):
        ratio = f"{ratios[i-1]:.6f}" if i > 0 else "-"
        print(f"{n_points:>8} {errors[i]:>20.6e} {ratio:>15}")

    # Verify decreasing approximation error.
    assert np.all(np.diff(errors) < 0)

    # Verify second-order convergence within a 1% tolerance.
    assert np.allclose(ratios, 4.0, rtol=0.01)    



if __name__ == "__main__":
    test_circle_curvature()
    test_curvature_convergence()
