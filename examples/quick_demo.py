"""
VGT Quick Demo
March 2025

This script demonstrates basic VGT simulations.
Run this to generate sample results quickly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import simulation modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'simulations'))
import vgt_1d_simulation
import vgt_2d_simulation
VGTSimulation1D = vgt_1d_simulation.VGTSimulation1D
VGTSimulation2D = vgt_2d_simulation.VGTSimulation2D
import matplotlib.pyplot as plt

def run_quick_demo():
    """Run a quick demonstration of VGT simulations."""
    
    print("=" * 50)
    print("Vibrational Gravity Theory - Quick Demo")
    print("=" * 50)
    
    # 1D Demo
    print("\n1. Running 1D simulation...")
    sim_1d = VGTSimulation1D(L=10.0, Nx=200, omega0=2.0)
    sim_1d.simulate(Nt=100, save_every=10)
    
    print("   - Field evolution computed")
    print(f"   - Max amplitude: {max(sim_1d.max_amplitude):.4f}")
    print(f"   - Final energy: {sim_1d.max_amplitude[-1]:.4f}")
    
    # Simple plot
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(sim_1d.x, sim_1d.phi_history[0], 'b-', label='Initial')
    plt.plot(sim_1d.x, sim_1d.phi_history[-1], 'r--', label='Final')
    plt.xlabel('Position x')
    plt.ylabel('Field φ')
    plt.title('1D Field Evolution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(sim_1d.max_amplitude, 'g-')
    plt.xlabel('Time steps')
    plt.ylabel('Max |φ|')
    plt.title('Amplitude Evolution')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/quick_demo_1d.png', dpi=150)
    print("   - Saved plot to data/quick_demo_1d.png")
    
    # 2D Demo (smaller for speed)
    print("\n2. Running 2D simulation (reduced resolution)...")
    sim_2d = VGTSimulation2D(Lx=10, Ly=10, Nx=50, Ny=50, omega0=2.0)
    sim_2d.simulate(Nt=30, save_every=10, initial_type='gaussian')
    
    print("   - 2D field evolution computed")
    print(f"   - Number of snapshots: {len(sim_2d.phi_history)}")
    
    # Simple 2D visualization
    plt.figure(figsize=(10, 4))
    
    plt.subplot(1, 2, 1)
    plt.contourf(sim_2d.X, sim_2d.Y, sim_2d.phi_history[0], levels=20, cmap='RdBu')
    plt.colorbar(label='φ')
    plt.title('Initial Field')
    plt.xlabel('x')
    plt.ylabel('y')
    
    plt.subplot(1, 2, 2)
    plt.contourf(sim_2d.X, sim_2d.Y, sim_2d.phi_history[-1], levels=20, cmap='RdBu')
    plt.colorbar(label='φ')
    plt.title('Final Field')
    plt.xlabel('x')
    plt.ylabel('y')
    
    plt.tight_layout()
    plt.savefig('data/quick_demo_2d.png', dpi=150)
    print("   - Saved plot to data/quick_demo_2d.png")
    
    print("\n" + "=" * 50)
    print("Demo complete! Check the 'data' folder for outputs.")
    print("=" * 50)
    
    return sim_1d, sim_2d


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run the demo
    sim_1d, sim_2d = run_quick_demo()
    
    # Show plots (optional - comment out for non-interactive mode)
    plt.show()
