import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict

def generate_sample_data(shift: str, days: int = 7) -> List[Dict]:
    """Generate sample data for analytics"""
    data = []
    
    # Base patterns for different shifts
    shift_patterns = {
        "night": {"base_count": 80, "variance": 20, "efficiency": 0.85},
        "morning": {"base_count": 120, "variance": 30, "efficiency": 0.95},
        "afternoon": {"base_count": 100, "variance": 25, "efficiency": 0.90}
    }
    
    pattern = shift_patterns.get(shift, {"base_count": 100, "variance": 25, "efficiency": 0.9})
    
    for day in range(days):
        # Generate daily data
        base_count = pattern["base_count"]
        variance = pattern["variance"]
        efficiency = pattern["efficiency"]
        
        # Add some randomness
        pallet_count = max(20, int(base_count + random.uniform(-variance, variance)))
        
        # Generate station breakdown
        tube_pallets = int(pallet_count * 0.6)
        non_tube_pallets = pallet_count - tube_pallets
        
        # Distribute among stations
        tube_distribution = distribute_pallets(tube_pallets, 4)
        non_tube_distribution = distribute_pallets(non_tube_pallets, 2)
        
        # Create data entries
        for i, count in enumerate(tube_distribution, 1):
            if count > 0:
                processing_time = count * 15 / efficiency  # 15 min per pallet
                delay = max(0, processing_time - (count * 15))  # Delay calculation
                
                data.append({
                    "date": (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d"),
                    "shift": shift,
                    "station": f"Station Tube {i}",
                    "count": count,
                    "processing_time": processing_time,
                    "delay_minutes": delay,
                    "efficiency": efficiency
                })
        
        for i, count in enumerate(non_tube_distribution, 5):
            if count > 0:
                processing_time = count * 20 / efficiency  # 20 min per pallet
                delay = max(0, processing_time - (count * 20))
                
                data.append({
                    "date": (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d"),
                    "shift": shift,
                    "station": f"Station Non-Tube {i}",
                    "count": count,
                    "processing_time": processing_time,
                    "delay_minutes": delay,
                    "efficiency": efficiency
                })
    
    return data

def distribute_pallets(total_pallets: int, num_stations: int) -> List[int]:
    """Distribute pallets among stations"""
    base_distribution = total_pallets // num_stations
    remainder = total_pallets % num_stations
    
    distribution = [base_distribution] * num_stations
    
    # Add remainder randomly
    for i in range(remainder):
        distribution[i] += 1
    
    # Add some randomness (±15%)
    for i in range(len(distribution)):
        variation = int(distribution[i] * 0.15 * random.uniform(-1, 1))
        distribution[i] = max(0, distribution[i] + variation)
    
    return distribution

def generate_realtime_data() -> Dict:
    """Generate real-time data for dashboard"""
    current_time = datetime.now()
    hour = current_time.hour
    
    # Determine current shift
    if 22 <= hour or hour < 6:
        current_shift = "night"
        base_count = 80
    elif 6 <= hour < 14:
        current_shift = "morning"
        base_count = 120
    else:
        current_shift = "afternoon"
        base_count = 100
    
    # Generate real-time metrics
    active_pallets = random.randint(int(base_count * 0.3), int(base_count * 0.8))
    
    # Generate station status
    stations_status = {}
    stations = {
        "loading_dock": {"capacity": 100, "name": "Loading Dock"},
        "tube_1": {"capacity": 20, "name": "Station Tube 1"},
        "tube_2": {"capacity": 20, "name": "Station Tube 2"},
        "tube_3": {"capacity": 20, "name": "Station Tube 3"},
        "tube_4": {"capacity": 20, "name": "Station Tube 4"},
        "non_tube_5": {"capacity": 15, "name": "Station Non-Tube 5"},
        "non_tube_6": {"capacity": 15, "name": "Station Non-Tube 6"},
        "rms_a": {"capacity": 50, "name": "RMS A"},
        "rms_c": {"capacity": 50, "name": "RMS C"}
    }
    
    alerts = []
    
    for station_key, station_info in stations.items():
        utilization = random.uniform(0.2, 0.9)
        active_pallets_station = int(station_info["capacity"] * utilization)
        
        status = "operational"
        if utilization > 0.8:
            status = "high_utilization"
            alerts.append({
                "station": station_key,
                "type": "high_utilization",
                "message": f"Station {station_info['name']} is at {utilization:.1%} capacity",
                "severity": "warning" if utilization < 0.9 else "critical"
            })
        elif utilization < 0.1:
            status = "low_utilization"
        
        stations_status[station_key] = {
            "active_pallets": active_pallets_station,
            "capacity": station_info["capacity"],
            "utilization": utilization,
            "status": status
        }
    
    return {
        "timestamp": current_time.isoformat(),
        "shift": current_shift,
        "active_pallets": active_pallets,
        "stations_status": stations_status,
        "alerts": alerts,
        "efficiency": random.uniform(0.8, 0.98)
    }

def generate_historical_data(days: int = 30) -> List[Dict]:
    """Generate historical data for trend analysis"""
    data = []
    shifts = ["night", "morning", "afternoon"]
    
    for day in range(days):
        date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d")
        
        for shift in shifts:
            # Generate daily shift data
            shift_data = generate_sample_data(shift, 1)
            
            # Add date information
            for item in shift_data:
                item["date"] = date
            
            data.extend(shift_data)
    
    return data

def generate_3d_coordinates() -> Dict:
    """Generate 3D coordinates for visualization"""
    return {
        "loading_dock": {"x": 0, "y": 0, "z": 0, "name": "Loading Dock", "color": "#3B82F6"},
        "tube_1": {"x": 10, "y": 5, "z": 2, "name": "Station Tube 1", "color": "#10B981"},
        "tube_2": {"x": 15, "y": 5, "z": 2, "name": "Station Tube 2", "color": "#10B981"},
        "tube_3": {"x": 20, "y": 5, "z": 2, "name": "Station Tube 3", "color": "#10B981"},
        "tube_4": {"x": 25, "y": 5, "z": 2, "name": "Station Tube 4", "color": "#10B981"},
        "non_tube_5": {"x": 10, "y": -5, "z": 2, "name": "Station Non-Tube 5", "color": "#F59E0B"},
        "non_tube_6": {"x": 15, "y": -5, "z": 2, "name": "Station Non-Tube 6", "color": "#F59E0B"},
        "rms_a": {"x": 30, "y": 5, "z": 3, "name": "RMS A", "color": "#8B5CF6"},
        "rms_c": {"x": 30, "y": -5, "z": 3, "name": "RMS C", "color": "#8B5CF6"}
    }

def generate_prediction_data(pallet_count: int, shift: str, date: str) -> Dict:
    """Generate prediction data for given parameters"""
    # Calculate distribution
    tube_ratio = 0.6
    non_tube_ratio = 0.4
    
    tube_pallets = int(pallet_count * tube_ratio)
    non_tube_pallets = pallet_count - tube_pallets
    
    # Distribute among stations
    tube_distribution = distribute_pallets(tube_pallets, 4)
    non_tube_distribution = distribute_pallets(non_tube_pallets, 2)
    
    # Calculate efficiency based on shift
    shift_efficiencies = {"night": 0.85, "morning": 0.95, "afternoon": 0.90}
    efficiency = shift_efficiencies.get(shift, 0.9)
    
    prediction_data = {
        "date": date,
        "shift": shift,
        "total_pallets": pallet_count,
        "efficiency": efficiency,
        "stations": {
            "tube_stations": {},
            "non_tube_stations": {},
            "rms_stations": {}
        },
        "delays": {}
    }
    
    # Process tube stations
    for i, count in enumerate(tube_distribution, 1):
        processing_time = count * 15 / efficiency
        delay = max(0, processing_time - (count * 15))
        
        prediction_data["stations"]["tube_stations"][f"tube_{i}"] = {
            "pallet_count": count,
            "processing_time_minutes": processing_time,
            "delay_minutes": delay,
            "efficiency": efficiency
        }
    
    # Process non-tube stations
    for i, count in enumerate(non_tube_distribution, 5):
        processing_time = count * 20 / efficiency
        delay = max(0, processing_time - (count * 20))
        
        prediction_data["stations"]["non_tube_stations"][f"non_tube_{i}"] = {
            "pallet_count": count,
            "processing_time_minutes": processing_time,
            "delay_minutes": delay,
            "efficiency": efficiency
        }
    
    # Calculate RMS predictions
    rms_a_pallets = sum(tube_distribution)
    rms_c_pallets = sum(non_tube_distribution)
    
    rms_a_processing = rms_a_pallets * 10 / efficiency
    rms_c_processing = rms_c_pallets * 10 / efficiency
    
    prediction_data["stations"]["rms_stations"] = {
        "rms_a": {
            "pallet_count": rms_a_pallets,
            "processing_time_minutes": rms_a_processing,
            "delay_minutes": max(0, rms_a_processing - (rms_a_pallets * 10)),
            "efficiency": efficiency
        },
        "rms_c": {
            "pallet_count": rms_c_pallets,
            "processing_time_minutes": rms_c_processing,
            "delay_minutes": max(0, rms_c_processing - (rms_c_pallets * 10)),
            "efficiency": efficiency
        }
    }
    
    # Calculate overall delays
    total_delay = sum(
        station["delay_minutes"] 
        for station_type in prediction_data["stations"].values() 
        for station in station_type.values()
    )
    
    prediction_data["delays"] = {
        "total_delay_minutes": total_delay,
        "max_delay_minutes": max(
            station["delay_minutes"] 
            for station_type in prediction_data["stations"].values() 
            for station in station_type.values()
        ),
        "average_delay_minutes": total_delay / len([s for st in prediction_data["stations"].values() for s in st.values()])
    }
    
    return prediction_data 