"""
1D Vibrational Field Simulation
Vibrational Gravity Theory - March 2025
Author: Marc Moffat

Simulates the modified Klein-Gordon equation:
∂²φ/∂t² - c²∂²φ/∂x² + ω₀²φ = 0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import os

class VGTSimulation1D:
    def __init__(self, L=10.0, Nx=400, c=1.0, omega0=2.0, 
                 dt_factor=0.9, pulse_width=0.1):
        """
        Initialize 1D vibrational field simulation.
        
        Parameters:
        -----------
        L : float
            Domain length
        Nx : int
            Number of spatial grid points
        c : float
            Wave speed
        omega0 : float
            Intrinsic resonance frequency
        dt_factor : float
            CFL stability factor
        pulse_width : float
            Width of initial Gaussian pulse
        """
        self.L = L
        self.Nx = Nx
        self.c = c
        self.omega0 = omega0
        self.dx = L / Nx
        self.dt = dt_factor * self.dx / c
        self.pulse_width = pulse_width
        
        # Grid
        self.x = np.linspace(0, L, Nx)
        
        # Storage for results
        self.phi_history = []
        self.time_points = []
        self.max_amplitude = []
        
    def gaussian_pulse(self, center=None, amplitude=1.0):
        """Create Gaussian initial condition."""
        if center is None:
            center = self.L / 2
        return amplitude * np.exp(-((self.x - center)**2) / self.pulse_width)
    
    def simulate(self, Nt=300, save_every=10):
        """
        Run the simulation using finite difference method.
        
        Parameters:
        -----------
        Nt : int
            Number of time steps
        save_every : int
            Save field state every N steps
        """
        # Initialize field
        phi = self.gaussian_pulse()
        phi_prev = phi.copy()
        
        # Save initial state
        self.phi_history.append(phi.copy())
        self.time_points.append(0)
        self.max_amplitude.append(np.max(np.abs(phi)))
        
        # Time evolution
        for t in range(1, Nt + 1):
            phi_next = np.zeros_like(phi)
            
            # Interior points (second-order central difference)
            for i in range(1, self.Nx - 1):
                d2phi_dx2 = (phi[i+1] - 2*phi[i] + phi[i-1]) / self.dx**2
                phi_next[i] = (2*phi[i] - phi_prev[i] + 
                               self.dt**2 * (self.c**2 * d2phi_dx2 - 
                                           self.omega0**2 * phi[i]))
            
            # Fixed boundary conditions
            phi_next[0] = 0
            phi_next[-1] = 0
            
            # Update fields
            phi_prev = phi.copy()
            phi = phi_next.copy()
            
            # Store results
            if t % save_every == 0:
                self.phi_history.append(phi.copy())
                self.time_points.append(t * self.dt)
            
            self.max_amplitude.append(np.max(np.abs(phi)))
        
        return self
    
    def verify_dispersion(self):
        """Verify the modified dispersion relation ω² = c²k² + ω₀²"""
        # Take FFT of final state
        phi_final = self.phi_history[-1]
        phi_fft = fft(phi_final)
        k = fftfreq(self.Nx, self.dx) * 2 * np.pi
        
        # Theoretical dispersion
        omega_theory = np.sqrt(self.c**2 * k**2 + self.omega0**2)
        
        return k, phi_fft, omega_theory
    
    def plot_evolution(self, save_path=None):
        """Plot field evolution at different time points."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot snapshots
        n_snapshots = min(5, len(self.phi_history))
        indices = np.linspace(0, len(self.phi_history)-1, n_snapshots, dtype=int)
        
        for idx in indices:
            t = self.time_points[idx]
            phi = self.phi_history[idx]
            ax1.plot(self.x, phi, label=f't = {t:.2f}')
        
        ax1.set_xlabel('Position x')
        ax1.set_ylabel('Field amplitude φ(x,t)')
        ax1.set_title('Vibrational Field Evolution (1D)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot max amplitude over time
        time_full = np.arange(len(self.max_amplitude)) * self.dt
        ax2.plot(time_full, self.max_amplitude, 'b-', linewidth=2)
        ax2.set_xlabel('Time t')
        ax2.set_ylabel('Max |φ|')
        ax2.set_title('Peak Amplitude Evolution')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def plot_dispersion(self, save_path=None):
        """Plot dispersion relation verification."""
        k, phi_fft, omega_theory = self.verify_dispersion()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot FFT magnitude
        ax.plot(k[:self.Nx//2], np.abs(phi_fft[:self.Nx//2]), 
                'b.', label='Simulation FFT', markersize=4)
        
        # Theoretical curve
        k_theory = np.linspace(0, max(k[:self.Nx//2]), 100)
        omega_th = np.sqrt(self.c**2 * k_theory**2 + self.omega0**2)
        ax2 = ax.twinx()
        ax2.plot(k_theory, omega_th, 'r-', label='Theory: ω² = c²k² + ω₀²', 
                linewidth=2)
        
        ax.set_xlabel('Wave number k')
        ax.set_ylabel('|FFT(φ)|', color='b')
        ax2.set_ylabel('Frequency ω', color='r')
        ax.set_title(f'Dispersion Relation (ω₀ = {self.omega0})')
        
        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def save_data(self, directory='data/1d_results/'):
        """Save simulation data for later analysis."""
        os.makedirs(directory, exist_ok=True)
        
        # Save parameters
        params = {
            'L': self.L,
            'Nx': self.Nx,
            'c': self.c,
            'omega0': self.omega0,
            'dx': self.dx,
            'dt': self.dt,
            'pulse_width': self.pulse_width
        }
        
        np.savez(os.path.join(directory, 'simulation_data.npz'),
                 x=self.x,
                 phi_history=self.phi_history,
                 time_points=self.time_points,
                 max_amplitude=self.max_amplitude,
                 **params)
        
        print(f"Data saved to {directory}")


def run_parameter_sweep():
    """Run simulations for different omega0 values."""
    omega_values = [0.5, 1.0, 2.0, 4.0]
    results = []
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for i, omega0 in enumerate(omega_values):
        sim = VGTSimulation1D(omega0=omega0)
        sim.simulate(Nt=300)
        results.append(sim)
        
        # Plot on subplot
        ax = axes[i]
        for j in [0, len(sim.phi_history)//2, -1]:
            ax.plot(sim.x, sim.phi_history[j], 
                   label=f't = {sim.time_points[j]:.2f}')
        
        ax.set_title(f'ω₀ = {omega0}')
        ax.set_xlabel('x')
        ax.set_ylabel('φ')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Parameter Sweep: Varying Intrinsic Frequency ω₀')
    plt.tight_layout()
    plt.savefig('data/1d_results/parameter_sweep.png', dpi=300)
    plt.show()
    
    return results


if __name__ == "__main__":
    # Run basic simulation
    print("Running 1D Vibrational Field Simulation...")
    sim = VGTSimulation1D()
    sim.simulate(Nt=500, save_every=20)
    
    # Create visualizations
    print("Generating plots...")
    sim.plot_evolution(save_path='data/1d_results/wave_evolution.png')
    sim.plot_dispersion(save_path='data/1d_results/dispersion_relation.png')
    
    # Save data
    sim.save_data()
    
    # Run parameter sweep
    print("\nRunning parameter sweep...")
    run_parameter_sweep()
    
    print("\nSimulation complete!")