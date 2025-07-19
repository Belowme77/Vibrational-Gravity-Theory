# VGT Quick Start Guide

Welcome to the Vibrational Gravity Theory simulation framework! This guide will help you get started with running simulations and analyzing results.

## Installation

### Requirements
```bash
python >= 3.8
numpy >= 1.20
matplotlib >= 3.3
scipy >= 1.7
```

### Setup
```bash
# Clone the repository
git clone https://github.com/Belowme77/Vibrational-Gravity-Theory.git
cd Vibrational-Gravity-Theory

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Run Your First 1D Simulation

```python
from simulations.wave_1d import VGTSimulation1D

# Create simulation with default parameters
sim = VGTSimulation1D(
    L=10.0,           # Domain length
    Nx=400,           # Grid points
    omega0=2.0,       # Intrinsic frequency
    c=1.0            # Wave speed
)

# Run simulation
sim.simulate(Nt=500)

# Visualize results
sim.plot_evolution()
sim.plot_dispersion()
```

### 2. Explore 2D Wave Propagation

```python
from simulations.wave_2d import VGTSimulation2D

# Ring pulse simulation
sim = VGTSimulation2D(omega0=3.0)
sim.simulate(Nt=150, initial_type='ring')

# Create visualizations
sim.plot_snapshots()
sim.create_animation('my_wave.gif')
```

### 3. Analyze Dispersion Relations

```python
from analysis.dispersion import DispersionAnalyzer

# Load and analyze data
analyzer = DispersionAnalyzer('data/1d_results/simulation_data.npz')
analyzer.plot_dispersion_verification()
analyzer.analyze_stability()
```

## Key Concepts

### The Modified Wave Equation
VGT is based on a modified Klein-Gordon equation:

```
∂²φ/∂t² - c²∇²φ + ω₀²φ = 0
```

Where:
- `φ` is the vibrational field
- `ω₀` is the intrinsic resonance frequency
- `c` is the wave speed

### Important Parameters

1. **Intrinsic Frequency (ω₀)**
   - Controls the "mass" of the field
   - Higher values = stronger deviation from standard waves
   - Typical range: 0.5 - 5.0

2. **CFL Factor**
   - Controls numerical stability
   - Must be < 1.0 for 1D, < 0.7 for 2D
   - Default: 0.9 (1D), 0.5 (2D)

3. **Domain Size**
   - Should be large enough to avoid boundary effects
   - Typical: 10-50 wavelengths

## Common Tasks

### Parameter Sweep
```python
# Test different intrinsic frequencies
for omega0 in [0.5, 1.0, 2.0, 4.0]:
    sim = VGTSimulation1D(omega0=omega0)
    sim.simulate()
    sim.save_data(f'data/sweep_omega{omega0}/')
```

### Compare with Theory
```python
# Verify dispersion relation
k, fft_data, omega_theory = sim.verify_dispersion()

# Plot comparison
plt.plot(k, omega_theory, 'r-', label='Theory: ω² = c²k² + ω₀²')
plt.plot(k, fft_data, 'b.', label='Simulation')
```

### Export for Analysis
```python
# Save all data
sim.save_data('my_results/')

# Load in external tool
import numpy as np
data = np.load('my_results/simulation_data.npz')
phi = data['phi_history']
```

## Troubleshooting

### Simulation Unstable?
- Reduce `dt_factor` (e.g., 0.5 instead of 0.9)
- Check boundary conditions
- Ensure initial condition is smooth

### Memory Issues?
- Reduce grid size (`Nx`, `Ny`)
- Save less frequently (`save_every` parameter)
- Use compressed output format

### Unexpected Results?
- Verify parameters match theory
- Check units consistency
- Compare with 1D before moving to 2D

## Example Projects

### 1. Resonance Detection
Study how the field responds near resonant frequencies:
```python
# Sweep around expected resonance
omega_m = 2.0  # Expected resonance
omegas = np.linspace(0.8*omega_m, 1.2*omega_m, 20)

for omega in omegas:
    sim = VGTSimulation1D(omega0=omega)
    sim.simulate()
    # Measure response amplitude
    response = np.max(sim.max_amplitude)
    print(f"ω = {omega:.2f}, Response = {response:.4f}")
```

### 2. Interference Patterns
Create and analyze wave interference:
```python
# Two-source interference
sim = VGTSimulation2D()
phi1 = sim.gaussian_pulse_2d(center=(10, 15))
phi2 = sim.gaussian_pulse_2d(center=(20, 15))
sim.phi_history = [phi1 + phi2]
sim.simulate()
```

### 3. Dark Matter Analog
Simulate scale-dependent effects:
```python
# Vary domain size to test scale dependence
for L in [10, 20, 50, 100]:
    sim = VGTSimulation1D(L=L, Nx=int(40*L))
    sim.simulate()
    # Analyze effective coupling at different scales
```

## Advanced Features

### Custom Initial Conditions
```python
def custom_pulse(x, params):
    """Create your own initial field configuration"""
    return np.sin(2*np.pi*x/params['wavelength']) * np.exp(-x**2/params['width']**2)

sim = VGTSimulation1D()
sim.phi = custom_pulse(sim.x, {'wavelength': 2.0, 'width': 1.0})
sim.simulate()
```

### Parallel Processing
```python
from multiprocessing import Pool

def run_single_sim(omega0):
    sim = VGTSimulation1D(omega0=omega0)
    sim.simulate()
    return sim.max_amplitude[-1]

# Run multiple simulations in parallel
with Pool() as pool:
    omega_values = np.linspace(0.5, 5.0, 20)
    results = pool.map(run_single_sim, omega_values)
```

### Real-Time Visualization
```python
import matplotlib.animation as animation

# Create live animation during simulation
fig, ax = plt.subplots()
line, = ax.plot([], [])

def animate(frame):
    sim.step()  # Single time step
    line.set_data(sim.x, sim.phi)
    return line,

ani = animation.FuncAnimation(fig, animate, frames=1000, blit=True)
plt.show()
```

## Connecting to Experiments

### Generate Experimental Predictions
```python
# Predict ultrasonic resonance signal
mass = 0.1  # kg
omega_m = mass * 3e8**2 / 1.054e-34  # Resonant frequency
print(f"Expected resonance at: {omega_m/1e6:.2f} MHz")

# Simulate response
sim = VGTSimulation1D(omega0=omega_m)
sim.simulate()
```

### Compare with LIGO Data
```python
# Analyze gravitational wave dispersion
from analysis.gw_analysis import analyze_dispersion

# Load LIGO strain data (example)
strain_data = load_ligo_data('GW150914')
k_obs, omega_obs = analyze_dispersion(strain_data)

# Compare with VGT prediction
omega_vgt = np.sqrt(c**2 * k_obs**2 + omega0**2)
```

## Best Practices

1. **Always verify stability**
   - Run short test simulations first
   - Check energy conservation

2. **Document parameters**
   - Save all simulation parameters with results
   - Use descriptive filenames

3. **Validate against theory**
   - Check limiting cases (ω₀ → 0 should give standard waves)
   - Verify dispersion relations

4. **Reproducibility**
   - Set random seeds if used
   - Version control your analysis scripts

## Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: See `/docs/` for detailed theory
- **Examples**: Check `/examples/` for more use cases

## Next Steps

1. Read the full thesis PDF for theoretical background
2. Explore the example notebooks in `/examples/`
3. Try modifying parameters to see their effects
4. Consider contributing your own analysis tools!

---

*Happy simulating! Remember: The universe doesn't just curve - it resonates.*