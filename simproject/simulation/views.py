from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import InitialGridRequestSerializer, GridEvolutionRequestSerializer
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64

from .tasks import simulate_heat_evolution_task
from celery.result import AsyncResult
from celery import states
from django.http import JsonResponse
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

@api_view(['POST'])
def simulate_heat_evolution_async(request):
    serializer = GridEvolutionRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    req = serializer.validated_data

    task = simulate_heat_evolution_task.delay(req)

    return Response({
        "task_id": task.id,
        "status": "submitted"
    }, status=202)


@api_view(['GET'])
def get_task_status(request, task_id):
    result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": result.status,
    }

    if result.status == states.FAILURE:
        # Ensure the exception is turned into a string
        response["error"] = str(result.result)
    elif result.status == states.SUCCESS:
        response["result"] = result.result

    return Response(response)



@api_view(['POST'])
def simulate_heat(request):
    serializer = InitialGridRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    req = serializer.validated_data

    w, h = req['widthNumber'], req['heightNumber']
    b = req['boundaryTemps']

    temp_grid = np.zeros((h, w))
    temp_grid[0, :] = b['top']
    temp_grid[-1, :] = b['bottom']
    temp_grid[:, 0] = b['left']
    temp_grid[:, -1] = b['right']

    image = generate_map(temp_grid)

    return Response({
        "grid": temp_grid.tolist(),
        "image": image
    })

