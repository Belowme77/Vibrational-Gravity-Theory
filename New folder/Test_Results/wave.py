import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -----------------------------
# 1. Simulation Parameters
# -----------------------------
L = 10.0             # spatial domain size (e.g., from x=0 to x=10)
Nx = 400             # number of spatial points
dx = L / Nx          # spatial step
c = 1.0              # wave propagation speed
omega0 = 2.0         # intrinsic resonant frequency
dt = 0.9 * dx / c    # time step (CFL condition ~ 0.9)
Nt = 300             # total number of time steps for the animation

# -----------------------------
# 2. Set Up the Spatial Grid
# -----------------------------
x = np.linspace(0, L, Nx)

# -----------------------------
# 3. Initial Conditions
# -----------------------------
# Gaussian pulse centered at x=L/2
phi = np.exp(-((x - L/2)**2) / 0.1)
phi_prev = phi.copy()  # assume zero initial velocity

# We'll store the updated values here
phi_next = np.zeros_like(phi)

# -----------------------------
# 4. Figure Setup
# -----------------------------
fig, ax = plt.subplots()
line, = ax.plot(x, phi, lw=2)
ax.set_ylim(-1.2, 1.2)  # adjust as needed
ax.set_xlabel('x')
ax.set_ylabel(r'$\phi(x,t)$')
ax.set_title('1D Vibrational Wave Simulation')

# -----------------------------
# 5. Update Function for Animation
# -----------------------------
def update(frame):
    global phi, phi_prev, phi_next
    
    # Finite difference update for the wave equation:
    # phi_next = 2*phi - phi_prev + dt^2 * (c^2 * d2phi/dx2 - omega0^2 * phi)
    
    # We'll update only the interior points: 1..(Nx-2)
    for i in range(1, Nx-1):
        d2phi_dx2 = (phi[i+1] - 2*phi[i] + phi[i-1]) / dx**2
        phi_next[i] = (2 * phi[i] - phi_prev[i] +
                       dt**2 * (c**2 * d2phi_dx2 - omega0**2 * phi[i]))
    
    # Boundary conditions (fixed): phi=0 at x=0 and x=L
    phi_next[0] = 0
    phi_next[-1] = 0
    
    # Shift time steps
    phi_prev, phi = phi, phi_next.copy()
    
    # Update the line data for plotting
    line.set_ydata(phi)
    return line,

# -----------------------------
# 6. Animation
# -----------------------------
ani = FuncAnimation(fig, update, frames=Nt, blit=True, interval=20)
plt.show()
