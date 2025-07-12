from celery import shared_task
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
import time
import logging

logger = logging.getLogger(__name__)

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
    return base64.b64encode(buf.read()).decode('utf-8')


@shared_task
def simulate_heat_evolution_task(req):
    start_time = time.time()

    w, h = req['widthNumber'], req['heightNumber']
    alpha, dt, steps = req['alpha'], req['dt'], req['steps']

    dx = req['physicalWidth'] / w
    dy = req['physicalHeight'] / h
    r_x = alpha * dt / dx**2
    r_y = alpha * dt / dy**2

    if r_x + r_y > 0.5:
        return {"error": "Unstable configuration. Reduce dt or increase resolution."}

    T = np.zeros((h, w))
    b = req['boundaryTemps']
    T[0, :] = b['top']
    T[-1, :] = b['bottom']
    T[:, 0] = b['left']
    T[:, -1] = b['right']

    for _ in range(steps):
        T_new = T.copy()
        T_new[1:-1, 1:-1] = T[1:-1, 1:-1] + r_x * (
            T[1:-1, 2:] - 2*T[1:-1,1:-1] + T[1:-1,:-2]
        ) + r_y * (
            T[2:,1:-1] - 2*T[1:-1,1:-1] + T[:-2,1:-1]
        )
        T = T_new
        T[0, :] = b['top']
        T[-1, :] = b['bottom']
        T[:, 0] = b['left']
        T[:, -1] = b['right']

        elapsed = time.time() - start_time
        if elapsed > 10:
            logger.warning("Simulation took too long: %.2fs", elapsed)

    image = generate_map(T)

    return {"image": image}
