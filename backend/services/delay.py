import numpy as np
from typing import List, Dict, Any
from models.schemas import PredictionRequest, DelayEntry

class DelayEstimator:
    def __init__(self):
        # AGV configuration constants
        self.agv_speed = 2.0  # meters per second
        self.agv_capacity = 1  # pallets per trip
        
        # Route distances (in meters)
        self.route_distances = {
            'tube_station_1': 150,
            'tube_station_2': 200,
            'tube_station_3': 250,
            'tube_station_4': 300,
            'non_tube_station_5': 180,
            'non_tube_station_6': 220,
            'rms_a': 400,
            'rms_c': 350
        }
        
        # AGV allocation per route
        self.agv_allocation = {
            'tube': 4,  # 4 AGVs for Tube stations
            'non_tube': 3  # 3 AGVs for Non-Tube stations
        }
    
    def _calculate_travel_time(self, route: str) -> float:
        """Calculate one-way travel time for a route"""
        distance = self.route_distances.get(route, 200)
        return distance / self.agv_speed  # seconds
    
    def _calculate_round_trip_time(self, route: str) -> float:
        """Calculate round-trip time including loading/unloading"""
        travel_time = self._calculate_travel_time(route)
        loading_time = 30  # seconds for loading
        unloading_time = 30  # seconds for unloading
        return travel_time * 2 + loading_time + unloading_time
    
    def _get_route_type(self, route: str) -> str:
        """Determine if route is tube or non-tube"""
        if 'tube' in route:
            return 'tube'
        elif 'non_tube' in route:
            return 'non_tube'
        elif route in ['rms_a']:
            return 'tube'  # RMS A is served by tube AGVs
        elif route in ['rms_c']:
            return 'non_tube'  # RMS C is served by non-tube AGVs
        else:
            return 'tube'  # Default
    
    def _calculate_agv_capacity_per_hour(self, route: str, agv_config: Dict[str, Any]) -> float:
        """Calculate AGV capacity for a route per hour"""
        route_type = self._get_route_type(route)
        num_agvs = self.agv_allocation[route_type]
        
        # Get AGV mode configuration
        agv_mode = agv_config.get('mode', 'single')
        
        if agv_mode == 'single':
            # Single AGV mode - all AGVs handle same material
            round_trip_time = self._calculate_round_trip_time(route)
            trips_per_hour = 3600 / round_trip_time  # seconds in hour / round trip time
            return num_agvs * trips_per_hour * self.agv_capacity
        
        elif agv_mode == 'dual':
            # Dual AGV mode - each AGV handles different material
            round_trip_time = self._calculate_round_trip_time(route)
            trips_per_hour = 3600 / round_trip_time
            return num_agvs * trips_per_hour * self.agv_capacity * 0.8  # 20% efficiency loss
        
        elif agv_mode == 'specialized':
            # Specialized mode - AGV 1 for material A, AGV 2 for material B
            round_trip_time = self._calculate_round_trip_time(route)
            trips_per_hour = 3600 / round_trip_time
            return (num_agvs / 2) * trips_per_hour * self.agv_capacity * 0.9  # 10% efficiency loss
        
        else:
            # Default to single mode
            round_trip_time = self._calculate_round_trip_time(route)
            trips_per_hour = 3600 / round_trip_time
            return num_agvs * trips_per_hour * self.agv_capacity
    
    def _calculate_queue_delay(self, demand: float, capacity: float) -> float:
        """Calculate delay due to queuing"""
        if capacity >= demand:
            return 0.0
        
        # Simple queuing model: delay = (demand - capacity) / capacity * 60 minutes
        excess_demand = demand - capacity
        delay_minutes = (excess_demand / capacity) * 60
        
        return max(0, delay_minutes)
    
    def estimate_delays(self, request: PredictionRequest) -> List[DelayEntry]:
        """Main delay estimation method"""
        delay_entries = []
        
        # Calculate total pallets per truck
        total_pallets_per_truck = {}
        for truck in request.trucks:
            total_pallets_per_truck[truck.truck_id] = truck.pallet_volume
        
        # Calculate delays for each route
        routes = ['tube_station_1', 'tube_station_2', 'tube_station_3', 'tube_station_4',
                 'non_tube_station_5', 'non_tube_station_6', 'rms_a', 'rms_c']
        
        for route in routes:
            route_type = self._get_route_type(route)
            
            # Calculate AGV capacity for this route
            agv_capacity = self._calculate_agv_capacity_per_hour(route, request.agv_config.per_hour)
            
            # Calculate demand based on truck pallets
            total_demand = sum(total_pallets_per_truck.values())
            
            # Distribute demand across routes based on route type
            if route_type == 'tube':
                # 60% of pallets go to tube routes
                route_demand = total_demand * 0.6 / 5  # 5 tube routes (4 stations + RMS A)
            else:
                # 40% of pallets go to non-tube routes
                route_demand = total_demand * 0.4 / 3  # 3 non-tube routes (2 stations + RMS C)
            
            # Calculate delay for this route
            delay_minutes = self._calculate_queue_delay(route_demand, agv_capacity)
            
            # Add delay entry for each truck
            for truck in request.trucks:
                # Distribute delay proportionally based on pallet volume
                truck_delay = delay_minutes * (truck.pallet_volume / total_demand)
                
                delay_entries.append(DelayEntry(
                    truck_id=truck.truck_id,
                    route=route,
                    delay_minutes=round(truck_delay, 2)
                ))
        
        return delay_entries
    
    def get_system_delays(self, request: PredictionRequest) -> Dict[str, float]:
        """Get overall system delay metrics"""
        delay_entries = self.estimate_delays(request)
        
        # Calculate average delays by route
        route_delays = {}
        for entry in delay_entries:
            if entry.route not in route_delays:
                route_delays[entry.route] = []
            route_delays[entry.route].append(entry.delay_minutes)
        
        # Calculate averages
        avg_delays = {}
        for route, delays in route_delays.items():
            avg_delays[route] = sum(delays) / len(delays)
        
        return avg_delays

# Global delay estimator instance
delay_estimator = DelayEstimator()

def estimate_delays(request: PredictionRequest) -> List[DelayEntry]:
    """Main delay estimation function"""
    return delay_estimator.estimate_delays(request) 