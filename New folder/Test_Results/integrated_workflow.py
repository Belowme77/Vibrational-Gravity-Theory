import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

# -----------------------------
# Simulation Functions
# -----------------------------

def simulate_wave(L=10.0, Nx=400, c=1.0, omega0=2.0, pulse_width=0.1):
    """
    Initialize the spatial grid and the initial condition for phi.
    Returns the spatial grid x, initial phi, and a copy of phi for the previous time step.
    """
    dx = L / Nx
    x = np.linspace(0, L, Nx)
    # Gaussian pulse centered at L/2
    phi = np.exp(-((x - L/2)**2) / pulse_width)
    phi_prev = phi.copy()  # assume zero initial velocity
    return x, phi, phi_prev, dx

def update_wave(phi, phi_prev, dt, dx, c, omega0):
    """
    Compute the next time step using a finite difference method for the wave equation.
    """
    Nx = len(phi)
    phi_next = np.zeros_like(phi)
    # Update interior points
    for i in range(1, Nx-1):
        d2phi_dx2 = (phi[i+1] - 2*phi[i] + phi[i-1]) / dx**2
        phi_next[i] = 2 * phi[i] - phi_prev[i] + dt**2 * (c**2 * d2phi_dx2 - omega0**2 * phi[i])
    # Fixed boundary conditions: phi=0 at the edges
    phi_next[0] = 0
    phi_next[-1] = 0
    return phi_next

def run_simulation(L=10.0, Nx=400, c=1.0, omega0=2.0, Nt=300, pulse_width=0.1):
    """
    Run the simulation over Nt time steps and return the spatial grid and the history of phi.
    """
    x, phi, phi_prev, dx = simulate_wave(L, Nx, c, omega0, pulse_width)
    # Choose time step dt using CFL condition: dt = 0.9*dx/c
    dt = 0.9 * dx / c
    phi_history = [phi.copy()]
    for t in range(Nt):
        phi_next = update_wave(phi, phi_prev, dt, dx, c, omega0)
        phi_prev, phi = phi.copy(), phi_next.copy()
        phi_history.append(phi.copy())
    return x, np.array(phi_history), dt, dx

def plot_simulation(x, phi_history, filename="simulation_plot.png"):
    """
    Plot the final state of the simulation and save the plot.
    """
    plt.figure()
    plt.plot(x, phi_history[-1])
    plt.xlabel("x")
    plt.ylabel(r"$\phi(x)$")
    plt.title("Final State of the 1D Simulation")
    plt.savefig(filename)
    plt.show()

def animate_simulation(x, phi_history):
    """
    Animate the simulation using Matplotlib's FuncAnimation.
    """
    fig, ax = plt.subplots()
    line, = ax.plot(x, phi_history[0], lw=2)
    ax.set_ylim(np.min(phi_history) - 0.1, np.max(phi_history) + 0.1)
    ax.set_xlabel("x")
    ax.set_ylabel(r"$\phi(x,t)$")
    ax.set_title("1D Vibrational Wave Simulation")
    
    def update(frame):
        line.set_ydata(phi_history[frame])
        return line,
    
    ani = FuncAnimation(fig, update, frames=len(phi_history), interval=20, blit=True)
    plt.show()

def fourier_analysis(phi, dx):
    """
    Perform Fourier analysis on the provided phi array.
    Returns the positive frequencies and corresponding amplitude spectrum.
    """
    fft_vals = np.fft.fft(phi)
    freqs = np.fft.fftfreq(len(phi), d=dx)
    pos = freqs > 0
    return freqs[pos], np.abs(fft_vals)[pos]

def plot_fourier(freqs, fft_vals, filename="fourier_plot.png"):
    """
    Plot the Fourier spectrum on a log-log scale and save the plot.
    """
    plt.figure()
    plt.loglog(freqs, fft_vals)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title("Fourier Spectrum of the Final State")
    plt.savefig(filename)
    plt.show()

# -----------------------------
# Data Retrieval Functions
# -----------------------------

def retrieve_ligo_data(detector="H1", start_time=1126259462, duration=128):
    """
    Retrieve gravitational wave data from LIGO Open Science Center using gwpy.
    Requires gwpy to be installed.
    """
    from gwpy.timeseries import TimeSeries
    data = TimeSeries.fetch_open_data(detector, start_time, start_time + duration)
    return data

# -----------------------------
# Report Generation Function
# -----------------------------

def generate_report(sim_params, simulation_files, report_filename="results_summary.md"):
    """
    Generate a markdown report summarizing simulation parameters and results.
    sim_params: dictionary of simulation parameters.
    simulation_files: list of filenames for attached plots.
    """
    with open(report_filename, "w") as f:
        f.write("# Vibrational Gravity Theory Simulation Results\n\n")
        f.write("## Simulation Parameters\n")
        for key, value in sim_params.items():
            f.write(f"- **{key}**: {value}\n")
        f.write("\n## Attached Plots\n")
        for file in simulation_files:
            f.write(f"- {file}\n")
        f.write("\n## Summary\n")
        f.write("The simulation shows the evolution of the 1D wave equation with an intrinsic resonant frequency. ")
        f.write("Fourier analysis reveals the frequency content, and the results can be compared to the theoretical dispersion relation.\n")
    print(f"Report generated: {report_filename}")

# -----------------------------
# Main Function to Integrate Workflow
# -----------------------------

def main():
    # Run simulation
    print("Running 1D simulation...")
    x, phi_history, dt, dx = run_simulation(L=10.0, Nx=400, c=1.0, omega0=2.0, Nt=300, pulse_width=0.1)
    
    # Save final state plot
    sim_plot_file = "simulation_plot.png"
    plot_simulation(x, phi_history, filename=sim_plot_file)
    
    # Animate simulation (optional, will display interactively)
    animate_simulation(x, phi_history)
    
    # Fourier analysis on final state
    freqs, fft_vals = fourier_analysis(phi_history[-1], dx)
    fourier_plot_file = "fourier_plot.png"
    plot_fourier(freqs, fft_vals, filename=fourier_plot_file)
    
    # Retrieve example LIGO data
    try:
        print("Retrieving LIGO data...")
        ligo_data = retrieve_ligo_data(detector="H1", start_time=1126259462, duration=128)
        # Plot LIGO data and save
        ligo_plot_file = "ligo_data_plot.png"
        ligo_data.plot(title="LIGO H1 Data").savefig(ligo_plot_file)
        print("LIGO data plot saved as", ligo_plot_file)
    except Exception as e:
        print("Error retrieving LIGO data:", e)
    
    # Generate a simulation report in markdown format
    sim_params = {
        "Domain Length (L)": 10.0,
        "Number of Spatial Points (Nx)": 400,
        "Wave Speed (c)": 1.0,
        "Resonant Frequency (omega0)": 2.0,
        "Time Steps (Nt)": 300,
        "Time Step (dt)": dt,
        "Spatial Step (dx)": dx,
        "Pulse Width": 0.1
    }
    simulation_files = [sim_plot_file, fourier_plot_file]
    generate_report(sim_params, simulation_files, report_filename="results_summary.md")

if __name__ == "__main__":
    main()
