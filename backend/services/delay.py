"""Hourly fluid queues with conserved fleet allocation and persistent backlog."""
from models.schemas import ROUTES


def route_material(route):
    return 'non_tube' if route.startswith('non_tube') or route == 'rms_c' else 'tube'


def capacities(request):
    pools = {r: request.material_assignments[route_material(r)] for r in ROUTES}
    efficiency = {'single': 1.0, 'dual': 0.8, 'specialized': 0.9}[request.agv_config.mode]
    # Equal time-share allocation within each material pool: a fleet is never
    # counted in full on every route. Single-pallet trips, 2 m/s, 60 s handling.
    return {r: getattr(request.agv_config.per_hour, pools[r]) / list(pools.values()).count(pools[r])
            * 3600 / (2 * distance / 2.0 + 60) * efficiency for r, distance in ROUTES.items()}


def queue_series(demand, capacity):
    if capacity <= 0:
        raise ValueError('Capacity must be positive')
    backlog = 0.0
    result = []
    for volume in demand:
        if volume < 0:
            raise ValueError('Demand must be nonnegative')
        backlog = max(0.0, backlog + float(volume) - capacity)
        result.append({'backlog_pallets': round(backlog, 4),
                       'delay_minutes': round(backlog / capacity * 60, 4)})
    return result
