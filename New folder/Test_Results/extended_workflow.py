import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

# ---------------------------------------------------
# 1. 2D Simulation of the Modified Wave Equation
# Equation: phi_tt - c^2*(phi_xx + phi_yy) + omega0^2 * phi = 0
# ---------------------------------------------------

def initialize_2d_domain(L=10.0, Nx=200, Ny=200, pulse_width=0.1):
    """
    Initialize a 2D spatial grid and a Gaussian pulse centered at the domain center.
    Returns: x, y meshgrid, initial phi, and a copy for previous time step.
    """
    x = np.linspace(0, L, Nx)
    y = np.linspace(0, L, Ny)
    X, Y = np.meshgrid(x, y, indexing='ij')
    # Gaussian pulse centered at (L/2, L/2)
    phi = np.exp(-(((X - L/2)**2 + (Y - L/2)**2) / pulse_width))
    phi_prev = phi.copy()  # zero initial velocity
    return X, Y, phi, phi_prev

def update_2d(phi, phi_prev, dt, dx, dy, c, omega0):
    """
    Update the 2D wave field using a finite difference scheme.
    """
    Nx, Ny = phi.shape
    phi_next = np.zeros_like(phi)
    # Loop over interior grid points
    for i in range(1, Nx-1):
        for j in range(1, Ny-1):
            d2phi_dx2 = (phi[i+1, j] - 2*phi[i, j] + phi[i-1, j]) / dx**2
            d2phi_dy2 = (phi[i, j+1] - 2*phi[i, j] + phi[i, j-1]) / dy**2
            phi_next[i, j] = (2*phi[i, j] - phi_prev[i, j] +
                              dt**2 * (c**2 * (d2phi_dx2 + d2phi_dy2) - omega0**2 * phi[i, j]))
    # Apply fixed boundary conditions (phi = 0 on all edges)
    phi_next[0, :], phi_next[-1, :], phi_next[:, 0], phi_next[:, -1] = 0, 0, 0, 0
    return phi_next

def run_2d_simulation(L=10.0, Nx=200, Ny=200, c=1.0, omega0=2.0, Nt=300, pulse_width=0.1):
    """
    Run the 2D simulation over Nt time steps and return the meshgrid and history of phi.
    """
    X, Y, phi, phi_prev = initialize_2d_domain(L, Nx, Ny, pulse_width)
    dx = L / Nx
    dy = L / Ny
    # Set dt according to CFL: dt = 0.9*min(dx, dy)/c
    dt = 0.9 * min(dx, dy) / c
    phi_history = [phi.copy()]
    for t in range(Nt):
        phi_next = update_2d(phi, phi_prev, dt, dx, dy, c, omega0)
        phi_prev, phi = phi.copy(), phi_next.copy()
        phi_history.append(phi.copy())
    return X, Y, np.array(phi_history), dt, dx, dy

def plot_2d_final_state(X, Y, phi_final, filename="2d_final_state.png"):
    """
    Plot the final state of the 2D simulation and save the image.
    """
    plt.figure(figsize=(6,5))
    cp = plt.contourf(X, Y, phi_final, 50, cmap='viridis')
    plt.colorbar(cp)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("2D Simulation Final State")
    plt.savefig(filename)
    plt.show()

def animate_2d_simulation(X, Y, phi_history):
    """
    Animate the 2D simulation using contour plots.
    """
    fig, ax = plt.subplots(figsize=(6,5))
    cp = ax.contourf(X, Y, phi_history[0], 50, cmap='viridis')
    plt.colorbar(cp)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("2D Vibrational Wave Simulation")
    
    def update(frame):
        ax.clear()
        cp = ax.contourf(X, Y, phi_history[frame], 50, cmap='viridis')
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(f"2D Simulation - Frame {frame}")
        return cp.collections

    ani = FuncAnimation(fig, update, frames=len(phi_history), interval=50, blit=False)
    plt.show()

# ---------------------------------------------------
# 2. Fourier Analysis on a 1D Slice from the 2D Data
# ---------------------------------------------------

def fourier_analysis_slice(phi_final, dx):
    """
    Perform Fourier analysis on the central row of the final 2D state.
    Returns frequencies and amplitude spectrum.
    """
    central_row = phi_final[phi_final.shape[0]//2, :]
    fft_vals = np.fft.fft(central_row)
    freqs = np.fft.fftfreq(len(central_row), d=dx)
    pos = freqs > 0
    return freqs[pos], np.abs(fft_vals)[pos]

def plot_fourier_slice(freqs, fft_vals, filename="fourier_slice.png"):
    """
    Plot the Fourier spectrum of the central row on a log-log scale and save the plot.
    """
    plt.figure()
    plt.loglog(freqs, fft_vals)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title("Fourier Spectrum of Central Row")
    plt.savefig(filename)
    plt.show()

# ---------------------------------------------------
# 3. Parameter Sweep: Varying omega0
# ---------------------------------------------------

def parameter_sweep(L=10.0, Nx=200, Ny=200, c=1.0, omega0_values=[0, 2.0, 5.0], Nt=300, pulse_width=0.1):
    """
    Run the 2D simulation for a list of omega0 values and save the final state plots.
    Returns a dictionary mapping omega0 values to their final state phi arrays.
    """
    results = {}
    for omega0 in omega0_values:
        print(f"Running simulation for omega0 = {omega0}...")
        X, Y, phi_history, dt, dx, dy = run_2d_simulation(L, Nx, Ny, c, omega0, Nt, pulse_width)
        final_state = phi_history[-1]
        filename = f"2d_final_state_omega0_{omega0}.png"
        plot_2d_final_state(X, Y, final_state, filename)
        results[omega0] = {"final_state": final_state, "X": X, "Y": Y, "dx": dx}
    return results

# ---------------------------------------------------
# 4. Experimental Proposal Report Generation
# ---------------------------------------------------

def generate_experiment_report(sim_params, simulation_files, report_filename="experiment_report.md"):
    """
    Generate a markdown report summarizing simulation parameters, results, and experimental proposals.
    """
    with open(report_filename, "w") as f:
        f.write("# Vibrational Gravity Theory - Extended Simulation and Experimental Proposals\n\n")
        f.write("## Simulation Parameters\n")
        for key, value in sim_params.items():
            f.write(f"- **{key}**: {value}\n")
        f.write("\n## Generated Plots\n")
        for file in simulation_files:
            f.write(f"- {file}\n")
        f.write("\n## Experimental Proposals\n")
        f.write("1. **Acoustic/Ultrasonic Resonance Experiment:**\n")
        f.write("   - Design a table-top experiment using high-intensity ultrasonic transducers in a controlled environment.\n")
        f.write("   - Measure local gravitational acceleration variations using precision interferometry or torsion balances.\n")
        f.write("   - Compare measured frequency responses with the predictions from the vibrational gravity model.\n\n")
        f.write("2. **Superconducting System Experiment:**\n")
        f.write("   - Utilize superconducting materials under high-frequency electromagnetic stimulation to probe anomalous inertial or gravitational effects.\n")
        f.write("   - Measure weight or inertial changes using high-precision scales.\n\n")
        f.write("3. **Gravitational Wave Data Analysis:**\n")
        f.write("   - Analyze publicly available gravitational wave data (e.g., from LIGO) for signatures of additional resonant frequencies or phase shifts.\n")
        f.write("   - Use Fourier analysis to extract the frequency spectrum and compare with the theoretical dispersion relation.\n")
        f.write("\n## Summary\n")
        f.write("The extended simulations demonstrate how variations in the intrinsic resonant frequency impact the behavior of the 2D vibrational field. These results, combined with the outlined experimental proposals, provide a comprehensive plan for testing the vibrational gravity theory in both laboratory and astrophysical contexts.\n")
    print(f"Experimental proposal report generated: {report_filename}")

# ---------------------------------------------------
# 5. Main Integrated Workflow Function
# ---------------------------------------------------

def main():
    # Run a 2D simulation and animate (optional)
    print("Running a 2D simulation with omega0 = 2.0 ...")
    X, Y, phi_history, dt, dx, dy = run_2d_simulation(L=10.0, Nx=200, Ny=200, c=1.0, omega0=2.0, Nt=300, pulse_width=0.1)
    final_state = phi_history[-1]
    plot_2d_final_state(X, Y, final_state, filename="2d_final_state.png")
    # Uncomment the following line to see the animation:
    # animate_2d_simulation(X, Y, phi_history)
    
    # Perform Fourier analysis on a central row of the final state
    freqs, fft_vals = fourier_analysis_slice(final_state, dx)
    plot_fourier_slice(freqs, fft_vals, filename="fourier_slice.png")
    
    # Run parameter sweep for different omega0 values
    omega0_vals = [0, 2.0, 5.0]
    sweep_results = parameter_sweep(L=10.0, Nx=200, Ny=200, c=1.0, omega0_values=omega0_vals, Nt=300, pulse_width=0.1)
    
    # Collect simulation files for the report
    simulation_files = ["2d_final_state.png", "fourier_slice.png"]
    for omega0 in omega0_vals:
        simulation_files.append(f"2d_final_state_omega0_{omega0}.png")
    
    # Generate a markdown report including simulation parameters and experimental proposals
    sim_params = {
        "Domain Length (L)": 10.0,
        "Number of X Points (Nx)": 200,
        "Number of Y Points (Ny)": 200,
        "Wave Speed (c)": 1.0,
        "Resonant Frequency (omega0)": 2.0,
        "Time Steps (Nt)": 300,
        "Time Step (dt)": dt,
        "Spatial Steps (dx, dy)": (dx, dy),
        "Pulse Width": 0.1
    }
    generate_experiment_report(sim_params, simulation_files, report_filename="experiment_report.md")
    
if __name__ == "__main__":
    main()
