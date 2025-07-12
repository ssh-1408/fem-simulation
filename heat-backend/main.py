from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np

import matplotlib
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
import io
import base64


# --- Define models directly ---
class BoundaryTemps(BaseModel):
    top: float
    bottom: float
    left: float
    right: float

class InitialGridRequest(BaseModel):
    widthNumber: int
    heightNumber: int
    physicalWidth: float
    physicalHeight: float
    boundaryTemps: BoundaryTemps

class GridEvolutionRequest(InitialGridRequest):
    alpha: float
    dt: float
    steps: int  

class BoundaryPressure(BaseModel):
    inlet: float
    outlet: float

class FlowGridRequest(BaseModel):
    widthNumber: int
    heightNumber: int
    physicalWidth: float
    physicalHeight: float
    boundaryPressure: BoundaryPressure

class FlowEvolutionRequest(FlowGridRequest):
    viscosity: float
    dt: float
    steps: int 

# --- FastAPI app setup ---
application = FastAPI()

origins = [
    "http://localhost:4200", # For local Angular development
   
]

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- function for matplotlib ---
def generate_map(data: np.ndarray, title: str = "") -> str:
    fig, ax = plt.subplots(figsize=(8, 4))
    cax = ax.imshow(data, cmap='jet', origin='lower')
    fig.colorbar(cax)
    
    if title:
        ax.set_title(title)
    
    ax.set_xlabel("X points")
    ax.set_ylabel("Y points")

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64


# --- Endpoint ---
@application.post("/simulate")
def simulate_heat(req: InitialGridRequest):
    w, h = req.widthNumber, req.heightNumber
    top, bottom = req.boundaryTemps.top, req.boundaryTemps.bottom
    left, right = req.boundaryTemps.left, req.boundaryTemps.right

    temp_grid = np.zeros((h, w))

    # Set fixed boundary conditions
    temp_grid[0, :] = top
    temp_grid[-1, :] = bottom
    temp_grid[:, 0] = left
    temp_grid[:, -1] = right

    # Return the initial grid and image (no iteration yet)
    image = generate_map(temp_grid)

    return {
        "grid": temp_grid.tolist(),
        "image": image
    }


@application.post("/simulate_evolution")
def simulate_heat_evolution(req: GridEvolutionRequest):
    w, h = req.widthNumber, req.heightNumber
    alpha, dt, steps = req.alpha, req.dt, req.steps

    dx = req.physicalWidth / w
    dy = req.physicalHeight / h

    r_x = alpha * dt / dx**2
    r_y = alpha * dt / dy**2

    if r_x + r_y > 0.5:
        return {"error": "Unstable configuration. Reduce dt or increase resolution."}

    # Initialize temperature grid
    T = np.zeros((h, w))
    T[0, :] = req.boundaryTemps.top
    T[-1, :] = req.boundaryTemps.bottom
    T[:, 0] = req.boundaryTemps.left
    T[:, -1] = req.boundaryTemps.right

    for _ in range(steps):
        T_new = T.copy()
        T_new[1:-1, 1:-1] = T[1:-1, 1:-1] + r_x * (
            T[1:-1, 2:] - 2 * T[1:-1, 1:-1] + T[1:-1, :-2]
        ) + r_y * (
            T[2:, 1:-1] - 2 * T[1:-1, 1:-1] + T[:-2, 1:-1]
        )
        T = T_new
        # Re-apply boundaries
        T[0, :] = req.boundaryTemps.top
        T[-1, :] = req.boundaryTemps.bottom
        T[:, 0] = req.boundaryTemps.left
        T[:, -1] = req.boundaryTemps.right

    image = generate_map(T)

    return {
        "image": image
    }

@application.post("/simulate_flow")
def simulate_flow(req: FlowGridRequest):
    w, h = req.widthNumber, req.heightNumber
    dx = req.physicalWidth / w
    dp_dx = (req.boundaryPressure.outlet - req.boundaryPressure.inlet) / req.physicalWidth

    # Initial velocity in x, parabolic profile approximation
    y = np.linspace(0, req.physicalHeight, h)
    u_profile = (4 * (req.physicalHeight - y) * y) / (req.physicalHeight**2) * (-dp_dx)

    # Tile the profile across the width
    velocity_field = np.tile(u_profile.reshape(h, 1), (1, w))

    image = generate_map(velocity_field)

    return {
        "grid": velocity_field.tolist(),
        "image": image
    }

@application.post("/simulate_evolution_flow")
def simulate_evolution_flow(req: FlowEvolutionRequest):
    w, h = req.widthNumber, req.heightNumber
    nu, dt, steps = req.viscosity, req.dt, req.steps

    dx = req.physicalWidth / w
    dy = req.physicalHeight / h

    r_x = nu * dt / dx**2
    r_y = nu * dt / dy**2

    if r_x + r_y > 0.5:
        return {"error": "Unstable configuration. Reduce dt or increase resolution."}

    # Initialize velocity field with same parabolic profile
    y = np.linspace(0, req.physicalHeight, h)
    dp_dx = (req.boundaryPressure.outlet - req.boundaryPressure.inlet) / req.physicalWidth
    u_profile = (4 * (req.physicalHeight - y) * y) / (req.physicalHeight**2) * (-dp_dx)
    velocity = np.tile(u_profile.reshape(h, 1), (1, w))

    for _ in range(steps):
        u_new = velocity.copy()
        u_new[1:-1, 1:-1] = velocity[1:-1, 1:-1] + r_x * (
            velocity[1:-1, 2:] - 2 * velocity[1:-1, 1:-1] + velocity[1:-1, :-2]
        ) + r_y * (
            velocity[2:, 1:-1] - 2 * velocity[1:-1, 1:-1] + velocity[:-2, 1:-1]
        )
        velocity = u_new

        # Dirichlet: set top/bottom to zero (no-slip walls)
        velocity[0, :] = 0
        velocity[-1, :] = 0

    image = generate_map(velocity)
    return {
        "image": image
    }




