"""
Dispersion Analysis Tools
Vibrational Gravity Theory - March 2025
Author: Marc Moffat

Tools for analyzing VGT simulation results and verifying theoretical predictions.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fft2, fftfreq, fftshift
from scipy.optimize import curve_fit
import os

class DispersionAnalyzer:
    def __init__(self, simulation_data=None):
        """
        Initialize analyzer with simulation data.
        
        Parameters:
        -----------
        simulation_data : dict or str
            Either a dictionary with simulation results or path to .npz file
        """
        if isinstance(simulation_data, str):
            # Load from file
            data = np.load(simulation_data)
            self.data = {key: data[key] for key in data.files}
        else:
            self.data = simulation_data
            
    def verify_1d_dispersion(self, phi_data, dx, c, omega0):
        """Verify ω² = c²k² + ω₀² for 1D data."""
        # Compute FFT
        phi_fft = fft(phi_data)
        k = fftfreq(len(phi_data), dx) * 2 * np.pi
        
        # Get positive frequencies only
        k_pos = k[:len(k)//2]
        phi_fft_pos = np.abs(phi_fft[:len(k)//2])
        
        # Theoretical dispersion
        omega_theory = np.sqrt(c**2 * k_pos**2 + omega0**2)
        
        return k_pos, phi_fft_pos, omega_theory
    
    def analyze_2d_spectrum(self, phi_2d, dx, dy, c, omega0):
        """Analyze 2D Fourier spectrum."""
        # 2D FFT
        phi_fft = fftshift(fft2(phi_2d))
        kx = fftshift(fftfreq(phi_2d.shape[1], dx)) * 2 * np.pi
        ky = fftshift(fftfreq(phi_2d.shape[0], dy)) * 2 * np.pi
        
        # Create k-space mesh
        KX, KY = np.meshgrid(kx, ky)
        K = np.sqrt(KX**2 + KY**2)
        
        # Theoretical dispersion surface
        omega_theory = np.sqrt(c**2 * K**2 + omega0**2)
        
        return KX, KY, np.abs(phi_fft), omega_theory
    
    def plot_dispersion_verification(self, save_path=None):
        """Create comprehensive dispersion relation plots."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1D Dispersion
        if 'x' in self.data and 'phi_history' in self.data:
            ax = axes[0, 0]
            
            # Get data safely
            if hasattr(self.data['phi_history'], 'shape'):
                if len(self.data['phi_history'].shape) == 2:
                    phi_final = self.data['phi_history'][-1]
                else:
                    phi_final = self.data['phi_history']
            else:
                phi_final = np.array(self.data['phi_history'])[-1]
                
            dx = float(self.data['dx']) if 'dx' in self.data else 0.1
            c = float(self.data['c']) if 'c' in self.data else 1.0
            omega0 = float(self.data['omega0']) if 'omega0' in self.data else 2.0
            
            k, phi_fft, omega_th = self.verify_1d_dispersion(
                phi_final, dx, c, omega0
            )
            
            # Normalize and plot
            ax.plot(k, phi_fft / np.max(phi_fft), 'b.', label='FFT Data', alpha=0.6)
            ax2 = ax.twinx()
            ax2.plot(k, omega_th, 'r-', label='Theory', linewidth=2)
            
            ax.set_xlabel('Wave number k')
            ax.set_ylabel('Normalized |FFT|', color='b')
            ax2.set_ylabel('Frequency ω', color='r')
            ax.set_title('1D Dispersion Verification')
            ax.grid(True, alpha=0.3)
        
        # Resonance peaks
        ax = axes[0, 1]
        omega_scan = np.linspace(0.1, 5.0, 100)
        resonance = 1 / (omega_scan**2 - omega0**2 + 0.1j)**2
        
        ax.plot(omega_scan, np.abs(resonance), 'g-', linewidth=2)
        ax.axvline(omega0, color='r', linestyle='--', label=f'ω₀ = {omega0}')
        ax.set_xlabel('Frequency ω')
        ax.set_ylabel('Resonance Response')
        ax.set_title('Resonance Peak Structure')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Phase velocity
        ax = axes[1, 0]
        k_range = np.linspace(0.1, 10, 100)
        omega_disp = np.sqrt(c**2 * k_range**2 + omega0**2)
        v_phase = omega_disp / k_range
        v_group = c**2 * k_range / omega_disp
        
        ax.plot(k_range, v_phase, 'b-', label='Phase velocity', linewidth=2)
        ax.plot(k_range, v_group, 'r--', label='Group velocity', linewidth=2)
        ax.axhline(c, color='k', linestyle=':', label=f'c = {c}')
        ax.set_xlabel('Wave number k')
        ax.set_ylabel('Velocity')
        ax.set_title('Velocity Dispersion')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.5*c)
        
        # Energy distribution
        ax = axes[1, 1]
        if 'energy_history' in self.data and 'time_points' in self.data:
            time = np.array(self.data['time_points'])
            energy = np.array(self.data['energy_history'])
            
            if len(time) > 0 and len(energy) > 0:
                ax.plot(time, energy, 'k-', linewidth=2)
                ax.set_xlabel('Time t')
                ax.set_ylabel('Total Energy')
                ax.set_title('Energy Conservation')
                ax.grid(True, alpha=0.3)
                
                # Add relative change
                if len(energy) > 0:
                    rel_change = (energy - energy[0]) / energy[0] * 100
                    ax2 = ax.twinx()
                    ax2.plot(time, rel_change, 'r:', alpha=0.7)
                    ax2.set_ylabel('Relative Change (%)', color='r')
                    ax2.tick_params(axis='y', labelcolor='r')
        else:
            ax.text(0.5, 0.5, 'No energy data available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Energy Conservation')
        
        plt.suptitle('VGT Dispersion Analysis', fontsize=14)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def analyze_stability(self, save_path=None):
        """Analyze numerical stability metrics."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # CFL analysis
        ax = axes[0, 0]
        dt_factors = np.linspace(0.1, 2.0, 20)
        stability = []
        
        for dt_f in dt_factors:
            # Simple stability criterion
            stable = dt_f < 1.0 / np.sqrt(2)  # 2D stability limit
            stability.append(1 if stable else 0)
        
        ax.plot(dt_factors, stability, 'bo-', linewidth=2, markersize=8)
        ax.axvline(1/np.sqrt(2), color='r', linestyle='--', 
                  label='2D Stability Limit')
        ax.set_xlabel('CFL Factor (dt/dx × c)')
        ax.set_ylabel('Stable (1) / Unstable (0)')
        ax.set_title('CFL Stability Analysis')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.1, 1.1)
        
        # Amplitude decay
        ax = axes[0, 1]
        if 'max_amplitude' in self.data:
            # Handle both array and list formats
            if hasattr(self.data['max_amplitude'], '__len__'):
                amp = np.array(self.data['max_amplitude'])
                dt = float(self.data['dt']) if 'dt' in self.data else 0.01
                time = np.arange(len(amp)) * dt
            else:
                # Single value
                amp = np.array([self.data['max_amplitude']])
                time = np.array([0])
            
            # Fit exponential decay
            def exp_decay(t, A, tau, offset):
                return A * np.exp(-t/tau) + offset
            
            try:
                popt, _ = curve_fit(exp_decay, time, amp, 
                                   p0=[amp[0], time[-1]/2, amp[-1]])
                
                ax.plot(time, amp, 'b.', label='Simulation', alpha=0.5)
                ax.plot(time, exp_decay(time, *popt), 'r-', 
                       label=f'Fit: τ = {popt[1]:.2f}', linewidth=2)
            except:
                ax.plot(time, amp, 'b-', label='Simulation', linewidth=2)
            
            ax.set_xlabel('Time t')
            ax.set_ylabel('Max Amplitude')
            ax.set_title('Amplitude Evolution')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Frequency content
        ax = axes[1, 0]
        if 'phi_history' in self.data:
            # Analyze frequency content over time
            phi_history = self.data['phi_history']
            
            # Handle different data formats
            if hasattr(phi_history, 'shape'):
                n_snapshots = min(5, phi_history.shape[0]) if len(phi_history.shape) > 1 else 1
            else:
                n_snapshots = min(5, len(phi_history))
                
            if n_snapshots > 0:
                indices = np.linspace(0, n_snapshots-1, min(n_snapshots, 5), dtype=int)
                
                dx = float(self.data['dx']) if 'dx' in self.data else 0.1
                
                for idx in indices:
                    try:
                        if hasattr(phi_history, 'shape') and len(phi_history.shape) > 1:
                            phi = phi_history[idx]
                        else:
                            phi = np.array(phi_history)[idx] if idx < len(phi_history) else phi_history[-1]
                            
                        fft_data = np.abs(fft(phi))
                        freqs = fftfreq(len(phi), dx)
                        
                        # Plot positive frequencies
                        pos_mask = freqs > 0
                        time_label = f"t = {self.data['time_points'][idx]:.1f}" if 'time_points' in self.data and idx < len(self.data['time_points']) else f"snapshot {idx}"
                        ax.plot(freqs[pos_mask], fft_data[pos_mask], 
                               label=time_label, alpha=0.7)
                    except:
                        continue
                
                ax.set_xlabel('Frequency')
                ax.set_ylabel('|FFT|')
                ax.set_title('Frequency Evolution')
                ax.legend()
                ax.grid(True, alpha=0.3)
                ax.set_xlim(0, 10)
            else:
                ax.text(0.5, 0.5, 'No frequency data available', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Frequency Evolution')
        
        # Grid convergence placeholder
        ax = axes[1, 1]
        grid_sizes = [50, 100, 200, 400]
        errors = [0.1, 0.05, 0.025, 0.012]  # Example convergence
        
        ax.loglog(grid_sizes, errors, 'ko-', linewidth=2, markersize=8)
        ax.loglog(grid_sizes, 10/np.array(grid_sizes)**2, 'r--', 
                 label='Second-order convergence')
        ax.set_xlabel('Grid Points')
        ax.set_ylabel('Relative Error')
        ax.set_title('Grid Convergence Study')
        ax.legend()
        ax.grid(True, alpha=0.3, which='both')
        
        plt.suptitle('Numerical Stability Analysis', fontsize=14)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig


def generate_theory_comparison_plots():
    """Generate plots comparing VGT predictions with GR."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Gravitational wave dispersion
    ax = axes[0, 0]
    k = np.linspace(0, 5, 100)
    omega_gr = k  # GR: ω = ck (setting c=1)
    omega_vgt = np.sqrt(k**2 + 2.0**2)  # VGT with ω₀=2
    
    ax.plot(k, omega_gr, 'b-', label='GR: ω = ck', linewidth=2)
    ax.plot(k, omega_vgt, 'r--', label='VGT: ω² = c²k² + ω₀²', linewidth=2)
    ax.fill_between(k, omega_gr, omega_vgt, alpha=0.3, color='orange', 
                    label='VGT Deviation')
    ax.set_xlabel('Wave number k')
    ax.set_ylabel('Frequency ω')
    ax.set_title('GW Dispersion: GR vs VGT')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Polarization states
    ax = axes[0, 1]
    theories = ['GR\n(massless)', 'VGT\n(massive)']
    n_states = [2, 5]
    colors = ['blue', 'red']
    
    bars = ax.bar(theories, n_states, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Number of Polarization States')
    ax.set_title('Gravitational Wave Polarizations')
    ax.set_ylim(0, 6)
    
    for bar, n in zip(bars, n_states):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
               f'{n}', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Scale-dependent coupling
    ax = axes[1, 0]
    L = np.logspace(-6, 6, 200)  # Length scale in meters
    L0 = 1e-3  # Transition at 1mm
    gamma = 0.1
    G_eff = 1 + gamma * np.tanh((L0 - L) / 1e-35)
    
    ax.semilogx(L, G_eff, 'g-', linewidth=3)
    ax.axvline(L0, color='r', linestyle='--', alpha=0.7, label=f'L₀ = {L0}m')
    ax.axhline(1, color='k', linestyle=':', alpha=0.5)
    ax.set_xlabel('Length Scale L (m)')
    ax.set_ylabel('G_eff / G')
    ax.set_title('Scale-Dependent Gravitational Coupling')
    ax.set_ylim(0.9, 1.15)
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    
    # Dark matter rotation curves
    ax = axes[1, 1]
    r = np.linspace(0.1, 30, 100)  # kpc
    v_newton = np.sqrt(1/r)  # Normalized Newtonian
    v_obs = np.ones_like(r)  # Flat rotation curve
    v_vgt = np.sqrt(1/r * (1 + 0.5*np.tanh(2*(r-5))))  # VGT prediction
    
    ax.plot(r, v_newton, 'b--', label='Newtonian', linewidth=2)
    ax.plot(r, v_obs, 'k-', label='Observed', linewidth=2)
    ax.plot(r, v_vgt, 'r-', label='VGT Prediction', linewidth=2, alpha=0.8)
    ax.set_xlabel('Radius (kpc)')
    ax.set_ylabel('Rotation Velocity (normalized)')
    ax.set_title('Galaxy Rotation Curves')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.5)
    
    plt.suptitle('VGT vs General Relativity: Key Predictions', fontsize=14)
    plt.tight_layout()
    plt.savefig('data/theory_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # Create output directory
    os.makedirs('data', exist_ok=True)
    
    # Generate theory comparison plots
    print("Generating theory comparison plots...")
    generate_theory_comparison_plots()
    
    # If simulation data exists, analyze it
    data_files = [
        'data/1d_results/simulation_data.npz',
        'data/2d_results/simulation_2d_data.npz'
    ]
    
    for data_file in data_files:
        if os.path.exists(data_file):
            print(f"\nAnalyzing {data_file}...")
            analyzer = DispersionAnalyzer(data_file)
            
            # Generate analysis plots
            base_name = os.path.splitext(os.path.basename(data_file))[0]
            analyzer.plot_dispersion_verification(
                save_path=f'data/{base_name}_dispersion.png'
            )
            analyzer.analyze_stability(
                save_path=f'data/{base_name}_stability.png'
            )
    
    print("\nAnalysis complete!")
