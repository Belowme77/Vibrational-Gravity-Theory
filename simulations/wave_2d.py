"""
2D Vibrational Field Simulation
Vibrational Gravity Theory - March 2025
Author: Marc Moffat

Simulates 2D wave propagation with radial symmetry
∂²φ/∂t² - c²∇²φ + ω₀²φ = 0
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.ndimage import laplace
import os

class VGTSimulation2D:
    def __init__(self, Lx=20.0, Ly=20.0, Nx=200, Ny=200, 
                 c=1.0, omega0=2.0, dt_factor=0.5):
        """
        Initialize 2D vibrational field simulation.
        
        Parameters:
        -----------
        Lx, Ly : float
            Domain dimensions
        Nx, Ny : int
            Grid points in x and y
        c : float
            Wave speed
        omega0 : float
            Intrinsic resonance frequency
        dt_factor : float
            CFL stability factor (should be < 0.5 for 2D)
        """
        self.Lx = Lx
        self.Ly = Ly
        self.Nx = Nx
        self.Ny = Ny
        self.c = c
        self.omega0 = omega0
        
        self.dx = Lx / Nx
        self.dy = Ly / Ny
        self.dt = dt_factor * min(self.dx, self.dy) / c
        
        # Create mesh
        self.x = np.linspace(0, Lx, Nx)
        self.y = np.linspace(0, Ly, Ny)
        self.X, self.Y = np.meshgrid(self.x, self.y)
        
        # Storage
        self.phi_history = []
        self.time_points = []
        self.energy_history = []
        
    def gaussian_pulse_2d(self, center=None, width=1.0, amplitude=1.0):
        """Create 2D Gaussian initial condition."""
        if center is None:
            center = (self.Lx/2, self.Ly/2)
        
        r2 = (self.X - center[0])**2 + (self.Y - center[1])**2
        return amplitude * np.exp(-r2 / width**2)
    
    def ring_pulse(self, center=None, radius=3.0, width=0.5, amplitude=1.0):
        """Create ring-shaped initial condition."""
        if center is None:
            center = (self.Lx/2, self.Ly/2)
        
        r = np.sqrt((self.X - center[0])**2 + (self.Y - center[1])**2)
        return amplitude * np.exp(-((r - radius)**2) / width**2)
    
    def laplacian_2d(self, phi):
        """Compute 2D Laplacian using finite differences."""
        laplacian = np.zeros_like(phi)
        
        # Interior points
        laplacian[1:-1, 1:-1] = (
            (phi[1:-1, 2:] - 2*phi[1:-1, 1:-1] + phi[1:-1, :-2]) / self.dx**2 +
            (phi[2:, 1:-1] - 2*phi[1:-1, 1:-1] + phi[:-2, 1:-1]) / self.dy**2
        )
        
        return laplacian
    
    def simulate(self, Nt=200, save_every=10, initial_type='gaussian'):
        """
        Run 2D simulation.
        
        Parameters:
        -----------
        Nt : int
            Number of time steps
        save_every : int
            Save field every N steps
        initial_type : str
            'gaussian' or 'ring' initial condition
        """
        # Initialize field
        if initial_type == 'gaussian':
            phi = self.gaussian_pulse_2d()
        elif initial_type == 'ring':
            phi = self.ring_pulse()
        else:
            raise ValueError("Unknown initial_type")
        
        phi_prev = phi.copy()
        
        # Save initial state
        self.phi_history.append(phi.copy())
        self.time_points.append(0)
        self.energy_history.append(self.compute_energy(phi, phi_prev))
        
        # Time evolution
        for t in range(1, Nt + 1):
            # Compute Laplacian
            laplacian = self.laplacian_2d(phi)
            
            # Update field
            phi_next = (2*phi - phi_prev + 
                       self.dt**2 * (self.c**2 * laplacian - 
                                    self.omega0**2 * phi))
            
            # Fixed boundary conditions
            phi_next[0, :] = 0
            phi_next[-1, :] = 0
            phi_next[:, 0] = 0
            phi_next[:, -1] = 0
            
            # Update for next iteration
            phi_prev = phi.copy()
            phi = phi_next.copy()
            
            # Store results
            if t % save_every == 0:
                self.phi_history.append(phi.copy())
                self.time_points.append(t * self.dt)
                self.energy_history.append(self.compute_energy(phi, phi_prev))
        
        return self
    
    def compute_energy(self, phi, phi_prev):
        """Compute total field energy."""
        # Kinetic energy ~ (∂φ/∂t)²
        dphi_dt = (phi - phi_prev) / self.dt
        kinetic = 0.5 * np.sum(dphi_dt**2) * self.dx * self.dy
        
        # Potential energy ~ (∇φ)² + ω₀²φ²
        grad_x = np.gradient(phi, self.dx, axis=1)
        grad_y = np.gradient(phi, self.dy, axis=0)
        potential = 0.5 * np.sum(grad_x**2 + grad_y**2 + 
                                self.omega0**2 * phi**2) * self.dx * self.dy
        
        return kinetic + potential
    
    def plot_snapshots(self, indices=None, save_path=None):
        """Plot field snapshots at different times."""
        if indices is None:
            n_plots = min(6, len(self.phi_history))
            indices = np.linspace(0, len(self.phi_history)-1, n_plots, dtype=int)
        
        n_cols = 3
        n_rows = (len(indices) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4*n_rows))
        axes = axes.flatten() if n_rows > 1 else axes
        
        vmin = min(phi.min() for phi in self.phi_history)
        vmax = max(phi.max() for phi in self.phi_history)
        
        for i, idx in enumerate(indices):
            ax = axes[i]
            im = ax.contourf(self.X, self.Y, self.phi_history[idx], 
                           levels=20, cmap='RdBu', vmin=vmin, vmax=vmax)
            ax.set_title(f't = {self.time_points[idx]:.2f}')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_aspect('equal')
            plt.colorbar(im, ax=ax, label='φ')
        
        # Hide extra subplots
        for i in range(len(indices), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle(f'2D Vibrational Field Evolution (ω₀ = {self.omega0})')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def plot_radial_profile(self, save_path=None):
        """Plot radial profile showing ring propagation."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Get center
        cx, cy = self.Lx/2, self.Ly/2
        
        # Compute radial distance for each point
        R = np.sqrt((self.X - cx)**2 + (self.Y - cy)**2)
        
        # Plot radial profiles at different times
        n_times = min(5, len(self.phi_history))
        indices = np.linspace(0, len(self.phi_history)-1, n_times, dtype=int)
        
        for idx in indices:
            phi = self.phi_history[idx]
            t = self.time_points[idx]
            
            # Create radial bins
            r_bins = np.linspace(0, min(self.Lx, self.Ly)/2, 50)
            phi_radial = []
            
            for i in range(len(r_bins)-1):
                mask = (R >= r_bins[i]) & (R < r_bins[i+1])
                if np.any(mask):
                    phi_radial.append(np.mean(phi[mask]))
                else:
                    phi_radial.append(0)
            
            r_centers = (r_bins[:-1] + r_bins[1:]) / 2
            ax1.plot(r_centers, phi_radial, label=f't = {t:.2f}')
        
        ax1.set_xlabel('Radial distance r')
        ax1.set_ylabel('Average φ(r)')
        ax1.set_title('Radial Profile Evolution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot energy over time
        ax2.plot(self.time_points, self.energy_history, 'b-', linewidth=2)
        ax2.set_xlabel('Time t')
        ax2.set_ylabel('Total Energy')
        ax2.set_title('Energy Conservation')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def create_animation(self, filename='wave_2d.gif', fps=10):
        """Create animation of wave propagation."""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        vmin = min(phi.min() for phi in self.phi_history)
        vmax = max(phi.max() for phi in self.phi_history)
        
        im = ax.contourf(self.X, self.Y, self.phi_history[0], 
                        levels=20, cmap='RdBu', vmin=vmin, vmax=vmax)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_aspect('equal')
        plt.colorbar(im, ax=ax, label='φ')
        
        def animate(frame):
            ax.clear()
            im = ax.contourf(self.X, self.Y, self.phi_history[frame], 
                           levels=20, cmap='RdBu', vmin=vmin, vmax=vmax)
            ax.set_title(f'Time: {self.time_points[frame]:.2f}')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_aspect('equal')
            return [ax]
        
        anim = FuncAnimation(fig, animate, frames=len(self.phi_history), 
                           interval=1000/fps, blit=True)
        
        anim.save(filename, writer='pillow', fps=fps)
        plt.close()
        
        print(f"Animation saved to {filename}")
    
    def save_data(self, directory='data/2d_results/'):
        """Save simulation data."""
        os.makedirs(directory, exist_ok=True)
        
        params = {
            'Lx': self.Lx, 'Ly': self.Ly,
            'Nx': self.Nx, 'Ny': self.Ny,
            'c': self.c, 'omega0': self.omega0,
            'dx': self.dx, 'dy': self.dy, 'dt': self.dt
        }
        
        # Save as compressed arrays
        np.savez_compressed(
            os.path.join(directory, 'simulation_2d_data.npz'),
            X=self.X, Y=self.Y,
            phi_history=self.phi_history,
            time_points=self.time_points,
            energy_history=self.energy_history,
            **params
        )
        
        print(f"Data saved to {directory}")


def demonstrate_interference():
    """Demonstrate wave interference patterns."""
    sim = VGTSimulation2D(Lx=30, Ly=30, Nx=300, Ny=300, omega0=1.5)
    
    # Create two source points
    phi1 = sim.gaussian_pulse_2d(center=(10, 15), width=1.0, amplitude=0.7)
    phi2 = sim.gaussian_pulse_2d(center=(20, 15), width=1.0, amplitude=0.7)
    
    # Set as initial condition
    sim.phi_history = [phi1 + phi2]
    sim.time_points = [0]
    
    # Run simulation
    sim.simulate(Nt=150, save_every=5)
    
    # Plot interference patterns
    sim.plot_snapshots(save_path='data/2d_results/interference_pattern.png')
    
    return sim


if __name__ == "__main__":
    # Create output directory
    os.makedirs('data/2d_results', exist_ok=True)
    
    # Run basic Gaussian pulse simulation
    print("Running 2D Gaussian pulse simulation...")
    sim_gaussian = VGTSimulation2D()
    sim_gaussian.simulate(Nt=150, save_every=5, initial_type='gaussian')
    sim_gaussian.plot_snapshots(save_path='data/2d_results/gaussian_evolution.png')
    sim_gaussian.plot_radial_profile(save_path='data/2d_results/radial_profile.png')
    sim_gaussian.save_data()
    
    # Run ring pulse simulation
    print("\nRunning 2D ring pulse simulation...")
    sim_ring = VGTSimulation2D(omega0=3.0)
    sim_ring.simulate(Nt=150, save_every=5, initial_type='ring')
    sim_ring.plot_snapshots(save_path='data/2d_results/ring_propagation.png')
    sim_ring.create_animation('data/2d_results/ring_animation.gif')
    
    # Demonstrate interference
    print("\nDemonstrating interference patterns...")
    demonstrate_interference()
    
    print("\n2D simulations complete!")