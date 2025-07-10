import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class PalletMovementModel:
    def __init__(self):
        self.stations = {
            "loading_dock": {"name": "Loading Dock", "capacity": 100, "processing_time": 5},
            "tube_1": {"name": "Station Tube 1", "capacity": 20, "processing_time": 15},
            "tube_2": {"name": "Station Tube 2", "capacity": 20, "processing_time": 15},
            "tube_3": {"name": "Station Tube 3", "capacity": 20, "processing_time": 15},
            "tube_4": {"name": "Station Tube 4", "capacity": 20, "processing_time": 15},
            "non_tube_5": {"name": "Station Non-Tube 5", "capacity": 15, "processing_time": 20},
            "non_tube_6": {"name": "Station Non-Tube 6", "capacity": 15, "processing_time": 20},
            "rms_a": {"name": "RMS A", "capacity": 50, "processing_time": 10},
            "rms_c": {"name": "RMS C", "capacity": 50, "processing_time": 10}
        }
        
        # Historical data patterns
        self.shift_patterns = {
            "night": {"efficiency": 0.85, "delay_factor": 1.2},
            "morning": {"efficiency": 0.95, "delay_factor": 1.0},
            "afternoon": {"efficiency": 0.90, "delay_factor": 1.1}
        }
    
    def predict_movement(self, pallet_count: int, shift: str, date: str) -> Dict:
        """Predict pallet movement for given parameters"""
        
        # Calculate base distribution
        tube_ratio = 0.6  # 60% to tube stations
        non_tube_ratio = 0.4  # 40% to non-tube stations
        
        tube_pallets = int(pallet_count * tube_ratio)
        non_tube_pallets = pallet_count - tube_pallets
        
        # Distribute among stations
        tube_distribution = self._distribute_pallets(tube_pallets, 4)  # 4 tube stations
        non_tube_distribution = self._distribute_pallets(non_tube_pallets, 2)  # 2 non-tube stations
        
        # Calculate processing times and delays
        shift_efficiency = self.shift_patterns.get(shift, {"efficiency": 0.9, "delay_factor": 1.0})
        
        prediction_data = {
            "date": date,
            "shift": shift,
            "total_pallets": pallet_count,
            "stations": {
                "tube_stations": {},
                "non_tube_stations": {},
                "rms_stations": {}
            },
            "delays": {},
            "efficiency": shift_efficiency["efficiency"]
        }
        
        # Process tube stations
        for i, count in enumerate(tube_distribution, 1):
            station_key = f"tube_{i}"
            station_data = self._calculate_station_metrics(
                count, station_key, shift_efficiency
            )
            prediction_data["stations"]["tube_stations"][station_key] = station_data
        
        # Process non-tube stations
        for i, count in enumerate(non_tube_distribution, 5):
            station_key = f"non_tube_{i}"
            station_data = self._calculate_station_metrics(
                count, station_key, shift_efficiency
            )
            prediction_data["stations"]["non_tube_stations"][station_key] = station_data
        
        # Calculate RMS predictions
        rms_a_pallets = sum(tube_distribution)
        rms_c_pallets = sum(non_tube_distribution)
        
        rms_a_data = self._calculate_station_metrics(
            rms_a_pallets, "rms_a", shift_efficiency
        )
        rms_c_data = self._calculate_station_metrics(
            rms_c_pallets, "rms_c", shift_efficiency
        )
        
        prediction_data["stations"]["rms_stations"] = {
            "rms_a": rms_a_data,
            "rms_c": rms_c_data
        }
        
        # Calculate overall delays
        prediction_data["delays"] = self._calculate_overall_delays(prediction_data)
        
        return prediction_data
    
    def _distribute_pallets(self, total_pallets: int, num_stations: int) -> List[int]:
        """Distribute pallets among stations with some randomness"""
        base_distribution = total_pallets // num_stations
        remainder = total_pallets % num_stations
        
        distribution = [base_distribution] * num_stations
        
        # Add remainder randomly
        for i in range(remainder):
            distribution[i] += 1
        
        # Add some randomness (±10%)
        for i in range(len(distribution)):
            variation = int(distribution[i] * 0.1 * random.uniform(-1, 1))
            distribution[i] = max(0, distribution[i] + variation)
        
        return distribution
    
    def _calculate_station_metrics(self, pallet_count: int, station_key: str, shift_efficiency: Dict) -> Dict:
        """Calculate metrics for a specific station"""
        station = self.stations.get(station_key, {"capacity": 20, "processing_time": 15})
        
        # Calculate processing time with efficiency factor
        base_processing_time = station["processing_time"] * pallet_count
        actual_processing_time = base_processing_time / shift_efficiency["efficiency"]
        
        # Calculate delays
        capacity_delay = max(0, pallet_count - station["capacity"]) * 5  # 5 min per overflow pallet
        processing_delay = actual_processing_time - base_processing_time
        
        total_delay = capacity_delay + processing_delay
        
        return {
            "pallet_count": pallet_count,
            "capacity": station["capacity"],
            "processing_time_minutes": actual_processing_time,
            "delay_minutes": total_delay,
            "efficiency": shift_efficiency["efficiency"],
            "utilization": min(1.0, pallet_count / station["capacity"])
        }
    
    def _calculate_overall_delays(self, prediction_data: Dict) -> Dict:
        """Calculate overall delay metrics"""
        total_delay = 0
        max_delay = 0
        delayed_stations = 0
        
        # Calculate delays for all stations
        for station_type in ["tube_stations", "non_tube_stations", "rms_stations"]:
            for station_data in prediction_data["stations"][station_type].values():
                delay = station_data["delay_minutes"]
                total_delay += delay
                max_delay = max(max_delay, delay)
                if delay > 0:
                    delayed_stations += 1
        
        return {
            "total_delay_minutes": total_delay,
            "max_delay_minutes": max_delay,
            "delayed_stations_count": delayed_stations,
            "average_delay_minutes": total_delay / len(prediction_data["stations"]["tube_stations"]) if prediction_data["stations"]["tube_stations"] else 0
        }
    
    def get_station_breakdown(self, data: List[Dict]) -> Dict:
        """Get breakdown of pallets by station"""
        breakdown = {
            "loading_dock": 0,
            "tube_stations": {"1": 0, "2": 0, "3": 0, "4": 0},
            "non_tube_stations": {"5": 0, "6": 0},
            "rms_stations": {"A": 0, "C": 0}
        }
        
        for item in data:
            station = item.get("station", "")
            count = item.get("count", 0)
            
            if "tube" in station.lower():
                station_num = station.split()[-1]
                if station_num in breakdown["tube_stations"]:
                    breakdown["tube_stations"][station_num] += count
            elif "non-tube" in station.lower():
                station_num = station.split()[-1]
                if station_num in breakdown["non_tube_stations"]:
                    breakdown["non_tube_stations"][station_num] += count
            elif "rms" in station.lower():
                rms_id = station.split()[-1]
                if rms_id in breakdown["rms_stations"]:
                    breakdown["rms_stations"][rms_id] += count
            else:
                breakdown["loading_dock"] += count
        
        return breakdown
    
    def get_realtime_data(self, current_time: datetime) -> Dict:
        """Get real-time pallet movement data"""
        # Simulate real-time data
        hour = current_time.hour
        
        # Determine current shift
        if 22 <= hour or hour < 6:
            current_shift = "night"
        elif 6 <= hour < 14:
            current_shift = "morning"
        else:
            current_shift = "afternoon"
        
        # Generate real-time metrics
        realtime_data = {
            "timestamp": current_time.isoformat(),
            "shift": current_shift,
            "active_pallets": random.randint(50, 150),
            "stations_status": {},
            "alerts": []
        }
        
        # Generate station status
        for station_key, station_info in self.stations.items():
            utilization = random.uniform(0.3, 0.9)
            active_pallets = int(station_info["capacity"] * utilization)
            
            realtime_data["stations_status"][station_key] = {
                "active_pallets": active_pallets,
                "capacity": station_info["capacity"],
                "utilization": utilization,
                "status": "operational" if utilization < 0.8 else "high_utilization"
            }
            
            # Generate alerts for high utilization
            if utilization > 0.8:
                realtime_data["alerts"].append({
                    "station": station_key,
                    "type": "high_utilization",
                    "message": f"Station {station_info['name']} is at {utilization:.1%} capacity"
                })
        
        return realtime_data 