import numpy as np
import matplotlib.pyplot as plt

def simulate_1d(L=10.0, Nx=400, c=1.0, omega0=2.0, Nt=300, dt_factor=0.9, pulse_width=0.1):
    """
    Simulate the 1D modified wave equation:
      phi_tt = c^2 * phi_xx - omega0^2 * phi
    with fixed boundary conditions and a Gaussian initial pulse.
    
    Returns:
      x: spatial grid
      phi: final state of the field after Nt time steps
      max_amplitude: array of maximum amplitude at each time step
      dt: time step used in the simulation
    """
    dx = L / Nx
    dt = dt_factor * dx / c  # CFL condition scaled by dt_factor
    x = np.linspace(0, L, Nx)
    
    # Initial condition: Gaussian pulse centered at L/2
    phi = np.exp(-((x - L/2)**2) / pulse_width)
    phi_prev = phi.copy()  # initial velocity assumed zero
    
    max_amplitude = [np.max(np.abs(phi))]
    
    for t in range(Nt):
        phi_next = np.zeros_like(phi)
        # Update interior points using finite difference
        for i in range(1, Nx - 1):
            d2phi_dx2 = (phi[i+1] - 2*phi[i] + phi[i-1]) / dx**2
            phi_next[i] = 2*phi[i] - phi_prev[i] + dt**2 * (c**2 * d2phi_dx2 - omega0**2 * phi[i])
        # Fixed boundary conditions: phi = 0 at x = 0 and x = L
        phi_next[0] = 0
        phi_next[-1] = 0
        
        # Update for next time step
        phi_prev, phi = phi.copy(), phi_next.copy()
        max_amplitude.append(np.max(np.abs(phi)))
        
    return x, phi, np.array(max_amplitude), dt

def parameter_sweep_omega0(omega0_values, **kwargs):
    """
    Run the simulation for different omega0 values.
    
    Returns a dictionary mapping each omega0 value to its simulation results.
    """
    results = {}
    for omega0 in omega0_values:
        print(f"Running simulation for omega0 = {omega0}...")
        x, phi, max_amp, dt = simulate_1d(omega0=omega0, **kwargs)
        results[omega0] = {"x": x, "phi": phi, "max_amplitude": max_amp, "dt": dt}
    return results

def parameter_sweep_dt_factor(dt_factors, **kwargs):
    """
    Run the simulation for different dt_factor values.
    
    Returns a dictionary mapping each dt_factor to its simulation results.
    """
    results = {}
    for dt_factor in dt_factors:
        print(f"Running simulation for dt_factor = {dt_factor}...")
        x, phi, max_amp, dt = simulate_1d(dt_factor=dt_factor, **kwargs)
        results[dt_factor] = {"x": x, "phi": phi, "max_amplitude": max_amp, "dt": dt}
    return results

def plot_max_amplitude(sweep_results, param_name="omega0"):
    """
    Plot the maximum amplitude reached during the simulation as a function of the parameter.
    """
    param_values = []
    max_vals = []
    for key, res in sweep_results.items():
        param_values.append(key)
        max_vals.append(np.max(res["max_amplitude"]))
    
    plt.figure()
    plt.plot(param_values, max_vals, 'o-', markersize=8)
    plt.xlabel(param_name)
    plt.ylabel("Maximum Amplitude")
    plt.title(f"Max Amplitude vs {param_name}")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Run parameter sweep over omega0 values
    omega0_values = [0, 1, 2, 3, 5]
    sweep_omega0_results = parameter_sweep_omega0(omega0_values, L=10.0, Nx=400, c=1.0, Nt=300, dt_factor=0.9, pulse_width=0.1)
    plot_max_amplitude(sweep_omega0_results, param_name="omega0")
    
    # Run parameter sweep over dt_factor values for a fixed omega0
    dt_factors = [0.5, 0.7, 0.9, 1.1]
    sweep_dt_results = parameter_sweep_dt_factor(dt_factors, L=10.0, Nx=400, c=1.0, omega0=2.0, Nt=300, pulse_width=0.1)
    plot_max_amplitude(sweep_dt_results, param_name="dt_factor")
