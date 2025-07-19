"""
Complete VGT Demo
=================
This script demonstrates all major features of the VGT simulation framework.
Run this to verify your installation and see the theory in action.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simulations.wave_1d import VGTSimulation1D
    from simulations.wave_2d import VGTSimulation2D
    from analysis.dispersion import DispersionAnalyzer
except ImportError:
    # If running directly, add parent to path
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from simulations.wave_1d import VGTSimulation1D
    from simulations.wave_2d import VGTSimulation2D
    from analysis.dispersion import DispersionAnalyzer

def demo_1d_basic():
    """Basic 1D wave propagation demonstration."""
    print("\n=== 1D Basic Wave Propagation ===")
    
    # Create and run simulation
    sim = VGTSimulation1D(
        L=10.0,
        Nx=400,
        omega0=2.0,
        c=1.0,
        pulse_width=0.1
    )
    
    print(f"Running 1D simulation with ω₀ = {sim.omega0}")
    sim.simulate(Nt=500, save_every=20)
    
    # Create visualizations
    sim.plot_evolution(save_path='examples/output/1d_evolution.png')
    sim.plot_dispersion(save_path='examples/output/1d_dispersion.png')
    
    print("✓ 1D simulation complete!")
    return sim

def demo_resonance_sweep():
    """Demonstrate resonance behavior with frequency sweep."""
    print("\n=== Resonance Frequency Sweep ===")
    
    omega_values = np.linspace(0.5, 4.0, 8)
    max_amplitudes = []
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    
    for i, omega0 in enumerate(omega_values):
        # Run simulation
        sim = VGTSimulation1D(omega0=omega0, Nx=200)
        sim.simulate(Nt=300, save_every=50)
        
        # Record peak amplitude
        max_amp = np.max(sim.max_amplitude)
        max_amplitudes.append(max_amp)
        
        # Plot final state
        ax = axes[i]
        ax.plot(sim.x, sim.phi_history[-1], 'b-', linewidth=2)
        ax.set_title(f'ω₀ = {omega0:.1f}')
        ax.set_ylim(-1, 1)
        ax.grid(True, alpha=0.3)
        
        print(f"  ω₀ = {omega0:.1f}: Max amplitude = {max_amp:.3f}")
    
    plt.suptitle('VGT Field Response vs Intrinsic Frequency', fontsize=14)
    plt.tight_layout()
    plt.savefig('examples/output/resonance_sweep.png', dpi=150)
    plt.show()
    
    # Plot resonance curve
    plt.figure(figsize=(8, 6))
    plt.plot(omega_values, max_amplitudes, 'ro-', linewidth=2, markersize=8)
    plt.xlabel('Intrinsic Frequency ω₀')
    plt.ylabel('Maximum Field Amplitude')
    plt.title('Resonance Response Curve')
    plt.grid(True, alpha=0.3)
    plt.savefig('examples/output/resonance_curve.png', dpi=150)
    plt.show()
    
    print("✓ Resonance sweep complete!")

def demo_2d_patterns():
    """Demonstrate 2D wave patterns and interference."""
    print("\n=== 2D Wave Patterns ===")
    
    # Gaussian pulse propagation
    print("Creating 2D Gaussian pulse...")
    sim_gauss = VGTSimulation2D(Lx=20, Ly=20, Nx=150, Ny=150, omega0=2.0)
    sim_gauss.simulate(Nt=100, save_every=10, initial_type='gaussian')
    sim_gauss.plot_snapshots(
        indices=[0, 3, 6, 9],
        save_path='examples/output/2d_gaussian_evolution.png'
    )
    
    # Ring pulse propagation
    print("Creating 2D ring pulse...")
    sim_ring = VGTSimulation2D(Lx=20, Ly=20, Nx=150, Ny=150, omega0=3.0)
    sim_ring.simulate(Nt=100, save_every=10, initial_type='ring')
    sim_ring.plot_radial_profile(save_path='examples/output/2d_ring_profile.png')
    
    # Create animation
    print("Generating animation...")
    sim_ring.create_animation('examples/output/ring_wave.gif', fps=10)
    
    print("✓ 2D patterns complete!")
    return sim_gauss, sim_ring

def demo_interference():
    """Demonstrate wave interference in 2D."""
    print("\n=== Wave Interference Demo ===")
    
    sim = VGTSimulation2D(Lx=30, Ly=30, Nx=200, Ny=200, omega0=1.5)
    
    # Create two sources
    phi1 = sim.gaussian_pulse_2d(center=(10, 15), width=1.0, amplitude=0.7)
    phi2 = sim.gaussian_pulse_2d(center=(20, 15), width=1.0, amplitude=0.7)
    
    # Combine and set as initial condition
    sim.phi_history = [phi1 + phi2]
    sim.time_points = [0]
    
    # Run simulation
    sim.simulate(Nt=120, save_every=10)
    
    # Plot interference pattern
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    
    times_to_plot = [0, len(sim.phi_history)//3, 2*len(sim.phi_history)//3, -1]
    
    for i, idx in enumerate(times_to_plot):
        ax = axes[i//2, i%2]
        im = ax.contourf(sim.X, sim.Y, sim.phi_history[idx], 
                        levels=20, cmap='RdBu')
        ax.set_title(f't = {sim.time_points[idx]:.2f}')
        ax.set_aspect('equal')
        plt.colorbar(im, ax=ax)
    
    plt.suptitle('Two-Source Interference Evolution', fontsize=14)
    plt.tight_layout()
    plt.savefig('examples/output/interference_pattern.png', dpi=150)
    plt.show()
    
    print("✓ Interference demo complete!")

def demo_dispersion_analysis():
    """Analyze and verify the modified dispersion relation."""
    print("\n=== Dispersion Relation Analysis ===")
    
    # Generate high-resolution data
    sim = VGTSimulation1D(L=20.0, Nx=800, omega0=2.5)
    sim.simulate(Nt=1000, save_every=100)
    
    # Save data
    sim.save_data('examples/output/dispersion_test/')
    
    # Analyze
    analyzer = DispersionAnalyzer('examples/output/dispersion_test/simulation_data.npz')
    analyzer.plot_dispersion_verification(
        save_path='examples/output/dispersion_analysis.png'
    )
    
    print("✓ Dispersion analysis complete!")

def demo_vgt_vs_gr():
    """Compare VGT predictions with General Relativity."""
    print("\n=== VGT vs GR Comparison ===")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Gravitational wave dispersion
    ax = axes[0, 0]
    k = np.linspace(0, 5, 100)
    omega_gr = k  # GR: ω = ck (c=1)
    omega_vgt = np.sqrt(k**2 + 2.0**2)  # VGT with ω₀=2
    
    ax.plot(k, omega_gr, 'b-', label='GR: ω = ck', linewidth=2)
    ax.plot(k, omega_vgt, 'r--', label='VGT: ω² = c²k² + ω₀²', linewidth=2)
    ax.fill_between(k, omega_gr, omega_vgt, alpha=0.3, color='orange')
    ax.set_xlabel('Wave number k')
    ax.set_ylabel('Frequency ω')
    ax.set_title('Gravitational Wave Dispersion')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Phase velocity comparison
    ax = axes[0, 1]
    k_range = np.linspace(0.1, 10, 100)
    v_phase_gr = np.ones_like(k_range)  # c = 1 in GR
    v_phase_vgt = np.sqrt(1 + 4.0/k_range**2)  # ω₀ = 2
    
    ax.plot(k_range, v_phase_gr, 'b-', label='GR', linewidth=2)
    ax.plot(k_range, v_phase_vgt, 'r--', label='VGT', linewidth=2)
    ax.set_xlabel('Wave number k')
    ax.set_ylabel('Phase velocity v_p/c')
    ax.set_title('Phase Velocity Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.8, 2.0)
    
    # Polarization states
    ax = axes[1, 0]
    theories = ['General\nRelativity', 'Vibrational\nGravity']
    n_states = [2, 5]
    colors = ['blue', 'red']
    
    bars = ax.bar(theories, n_states, color=colors, alpha=0.7, width=0.6)
    ax.set_ylabel('Number of Polarization States')
    ax.set_title('Gravitational Wave Polarizations')
    ax.set_ylim(0, 6)
    
    for bar, n in zip(bars, n_states):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
               f'{n}', ha='center', va='bottom', fontsize=16, fontweight='bold')
    
    # Effective mass resonance
    ax = axes[1, 1]
    omega = np.linspace(0, 4, 200)
    omega_m = 2.0  # Resonant frequency
    gamma = 0.1
    m_eff = 1 - gamma * np.cos((omega - omega_m) * np.pi)**2
    
    ax.plot(omega, m_eff, 'g-', linewidth=3)
    ax.axvline(omega_m, color='r', linestyle='--', label=f'ω_m = {omega_m}')
    ax.set_xlabel('Applied Frequency ω')
    ax.set_ylabel('Effective Mass m_eff/m₀')
    ax.set_title('Resonant Mass Effect (VGT Prediction)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('VGT vs General Relativity: Key Differences', fontsize=14)
    plt.tight_layout()
    plt.savefig('examples/output/vgt_vs_gr.png', dpi=150)
    plt.show()
    
    print("✓ VGT vs GR comparison complete!")

def main():
    """Run all demonstrations."""
    print("=" * 50)
    print("VIBRATIONAL GRAVITY THEORY - COMPLETE DEMO")
    print("=" * 50)
    
    # Create output directory
    os.makedirs('examples/output', exist_ok=True)
    
    # Run all demos
    sim_1d = demo_1d_basic()
    demo_resonance_sweep()
    sim_gauss, sim_ring = demo_2d_patterns()
    demo_interference()
    demo_dispersion_analysis()
    demo_vgt_vs_gr()
    
    print("\n" + "=" * 50)
    print("ALL DEMONSTRATIONS COMPLETE!")
    print("Check examples/output/ for generated figures")
    print("=" * 50)
    
    # Summary statistics
    print("\nSummary:")
    print(f"- 1D grid points: {sim_1d.Nx}")
    print(f"- 2D grid points: {sim_gauss.Nx} × {sim_gauss.Ny}")
    print(f"- Intrinsic frequencies tested: 0.5 - 4.0")
    print(f"- Key prediction: 5 vs 2 polarization states")
    print(f"- Dispersion relation verified: ω² = c²k² + ω₀²")
    
    return sim_1d, sim_gauss, sim_ring

if __name__ == "__main__":
    main()
