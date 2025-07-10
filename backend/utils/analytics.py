import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta

def calculate_delays(data: List[Dict]) -> Dict:
    """Calculate delay metrics from data"""
    if not data:
        return {
            "total_delay_minutes": 0,
            "max_delay_minutes": 0,
            "average_delay_minutes": 0,
            "delayed_stations_count": 0,
            "delay_distribution": {}
        }
    
    delays = [item.get("delay_minutes", 0) for item in data]
    
    total_delay = sum(delays)
    max_delay = max(delays) if delays else 0
    average_delay = total_delay / len(delays) if delays else 0
    delayed_stations = len([d for d in delays if d > 0])
    
    # Calculate delay distribution
    delay_ranges = {
        "0-5": 0,
        "5-15": 0,
        "15-30": 0,
        "30+": 0
    }
    
    for delay in delays:
        if delay == 0:
            delay_ranges["0-5"] += 1
        elif delay <= 5:
            delay_ranges["0-5"] += 1
        elif delay <= 15:
            delay_ranges["5-15"] += 1
        elif delay <= 30:
            delay_ranges["15-30"] += 1
        else:
            delay_ranges["30+"] += 1
    
    return {
        "total_delay_minutes": total_delay,
        "max_delay_minutes": max_delay,
        "average_delay_minutes": average_delay,
        "delayed_stations_count": delayed_stations,
        "delay_distribution": delay_ranges,
        "delay_percentage": (delayed_stations / len(data)) * 100 if data else 0
    }

def calculate_efficiency(data: List[Dict]) -> Dict:
    """Calculate efficiency metrics from data"""
    if not data:
        return {
            "overall_efficiency": 0.9,
            "efficiency_by_station": {},
            "efficiency_trend": 0,
            "performance_score": 0
        }
    
    efficiencies = [item.get("efficiency", 0.9) for item in data]
    overall_efficiency = np.mean(efficiencies)
    
    # Calculate efficiency by station type
    station_efficiencies = {}
    for item in data:
        station = item.get("station", "")
        efficiency = item.get("efficiency", 0.9)
        
        if "tube" in station.lower():
            station_type = "tube"
        elif "non-tube" in station.lower():
            station_type = "non_tube"
        elif "rms" in station.lower():
            station_type = "rms"
        else:
            station_type = "other"
        
        if station_type not in station_efficiencies:
            station_efficiencies[station_type] = []
        station_efficiencies[station_type].append(efficiency)
    
    # Calculate average efficiency by station type
    efficiency_by_station = {}
    for station_type, eff_list in station_efficiencies.items():
        efficiency_by_station[station_type] = np.mean(eff_list)
    
    # Calculate efficiency trend (simplified)
    if len(efficiencies) > 1:
        efficiency_trend = np.polyfit(range(len(efficiencies)), efficiencies, 1)[0]
    else:
        efficiency_trend = 0
    
    # Calculate performance score (0-100)
    performance_score = overall_efficiency * 100
    
    return {
        "overall_efficiency": overall_efficiency,
        "efficiency_by_station": efficiency_by_station,
        "efficiency_trend": efficiency_trend,
        "performance_score": performance_score,
        "efficiency_grade": get_efficiency_grade(overall_efficiency)
    }

def get_efficiency_grade(efficiency: float) -> str:
    """Get efficiency grade based on efficiency score"""
    if efficiency >= 0.95:
        return "A+"
    elif efficiency >= 0.90:
        return "A"
    elif efficiency >= 0.85:
        return "B+"
    elif efficiency >= 0.80:
        return "B"
    elif efficiency >= 0.75:
        return "C+"
    elif efficiency >= 0.70:
        return "C"
    else:
        return "D"

def calculate_threshold_violations(data: List[Dict], threshold_pallets_per_hour: int) -> Dict:
    """Calculate threshold violations"""
    violations = []
    total_violations = 0
    
    for item in data:
        station = item.get("station", "")
        count = item.get("count", 0)
        processing_time = item.get("processing_time", 0)
        
        # Calculate pallets per hour
        hours = processing_time / 60  # Convert minutes to hours
        pallets_per_hour = count / hours if hours > 0 else 0
        
        if pallets_per_hour > threshold_pallets_per_hour:
            violation = {
                "station": station,
                "pallets_per_hour": pallets_per_hour,
                "threshold": threshold_pallets_per_hour,
                "violation_percentage": ((pallets_per_hour - threshold_pallets_per_hour) / threshold_pallets_per_hour) * 100,
                "severity": "high" if pallets_per_hour > threshold_pallets_per_hour * 1.5 else "medium"
            }
            violations.append(violation)
            total_violations += 1
    
    return {
        "total_violations": total_violations,
        "violations": violations,
        "violation_percentage": (total_violations / len(data)) * 100 if data else 0,
        "threshold": threshold_pallets_per_hour
    }

def calculate_trends(data: List[Dict], days: int = 7) -> Dict:
    """Calculate trends over time"""
    if not data:
        return {
            "efficiency_trend": 0,
            "delay_trend": 0,
            "volume_trend": 0,
            "prediction": {}
        }
    
    # Group data by date
    daily_data = {}
    for item in data:
        date = item.get("date", "")
        if date not in daily_data:
            daily_data[date] = []
        daily_data[date].append(item)
    
    # Calculate daily metrics
    daily_metrics = []
    dates = sorted(daily_data.keys())
    
    for date in dates:
        day_data = daily_data[date]
        
        avg_efficiency = np.mean([item.get("efficiency", 0.9) for item in day_data])
        avg_delay = np.mean([item.get("delay_minutes", 0) for item in day_data])
        total_volume = sum([item.get("count", 0) for item in day_data])
        
        daily_metrics.append({
            "date": date,
            "efficiency": avg_efficiency,
            "delay": avg_delay,
            "volume": total_volume
        })
    
    # Calculate trends
    if len(daily_metrics) > 1:
        dates_numeric = list(range(len(daily_metrics)))
        efficiencies = [m["efficiency"] for m in daily_metrics]
        delays = [m["delay"] for m in daily_metrics]
        volumes = [m["volume"] for m in daily_metrics]
        
        efficiency_trend = np.polyfit(dates_numeric, efficiencies, 1)[0]
        delay_trend = np.polyfit(dates_numeric, delays, 1)[0]
        volume_trend = np.polyfit(dates_numeric, volumes, 1)[0]
    else:
        efficiency_trend = delay_trend = volume_trend = 0
    
    # Simple prediction for next day
    if daily_metrics:
        latest = daily_metrics[-1]
        prediction = {
            "efficiency": max(0.5, min(1.0, latest["efficiency"] + efficiency_trend)),
            "delay": max(0, latest["delay"] + delay_trend),
            "volume": max(0, latest["volume"] + volume_trend)
        }
    else:
        prediction = {"efficiency": 0.9, "delay": 0, "volume": 100}
    
    return {
        "efficiency_trend": efficiency_trend,
        "delay_trend": delay_trend,
        "volume_trend": volume_trend,
        "prediction": prediction,
        "daily_metrics": daily_metrics
    }

def calculate_station_performance(data: List[Dict]) -> Dict:
    """Calculate performance metrics by station"""
    station_performance = {}
    
    for item in data:
        station = item.get("station", "")
        count = item.get("count", 0)
        processing_time = item.get("processing_time", 0)
        delay = item.get("delay_minutes", 0)
        efficiency = item.get("efficiency", 0.9)
        
        if station not in station_performance:
            station_performance[station] = {
                "total_pallets": 0,
                "total_processing_time": 0,
                "total_delay": 0,
                "efficiencies": [],
                "count": 0
            }
        
        station_performance[station]["total_pallets"] += count
        station_performance[station]["total_processing_time"] += processing_time
        station_performance[station]["total_delay"] += delay
        station_performance[station]["efficiencies"].append(efficiency)
        station_performance[station]["count"] += 1
    
    # Calculate averages and metrics
    for station, metrics in station_performance.items():
        count = metrics["count"]
        if count > 0:
            metrics["average_efficiency"] = np.mean(metrics["efficiencies"])
            metrics["average_processing_time"] = metrics["total_processing_time"] / count
            metrics["average_delay"] = metrics["total_delay"] / count
            metrics["pallets_per_shift"] = metrics["total_pallets"] / count
            metrics["performance_score"] = (metrics["average_efficiency"] * 100) - (metrics["average_delay"] * 0.5)
        else:
            metrics["average_efficiency"] = 0.9
            metrics["average_processing_time"] = 0
            metrics["average_delay"] = 0
            metrics["pallets_per_shift"] = 0
            metrics["performance_score"] = 90
    
    return station_performance

def generate_alert_thresholds() -> Dict:
    """Generate alert thresholds for monitoring"""
    return {
        "efficiency": {
            "warning": 0.85,
            "critical": 0.75
        },
        "delay": {
            "warning": 15,  # minutes
            "critical": 30   # minutes
        },
        "utilization": {
            "warning": 0.8,
            "critical": 0.9
        },
        "threshold_violation": {
            "warning": 0.1,  # 10% over threshold
            "critical": 0.3   # 30% over threshold
        }
    } 