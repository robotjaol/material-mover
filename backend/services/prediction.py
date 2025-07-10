import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
from models.schemas import PredictionRequest, ForecastEntry

class PredictionEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.xgb_model = None
        self.historical_data = self._load_sample_data()
    
    def _load_sample_data(self) -> pd.DataFrame:
        """Load sample historical data for training"""
        # Sample data: hourly pallet movements for June
        dates = pd.date_range('2024-06-01', '2024-06-30', freq='H')
        np.random.seed(42)
        
        data = {
            'timestamp': dates,
            'tube_station_1': np.random.poisson(15, len(dates)),
            'tube_station_2': np.random.poisson(12, len(dates)),
            'tube_station_3': np.random.poisson(10, len(dates)),
            'tube_station_4': np.random.poisson(8, len(dates)),
            'non_tube_station_5': np.random.poisson(20, len(dates)),
            'non_tube_station_6': np.random.poisson(18, len(dates)),
            'rms_a': np.random.poisson(45, len(dates)),
            'rms_c': np.random.poisson(38, len(dates))
        }
        return pd.DataFrame(data)
    
    def _prepare_features(self, request: PredictionRequest) -> pd.DataFrame:
        """Prepare features for ML model"""
        features = []
        
        # Extract truck and pallet information
        total_pallets = sum(truck.pallet_volume for truck in request.trucks)
        num_trucks = len(request.trucks)
        
        # AGV configuration features
        agv_mode = request.agv_config.mode
        agv_per_hour = request.agv_config.per_hour
        
        # Create feature matrix for each hour
        for hour in range(12):
            hour_features = {
                'hour': hour,
                'total_pallets': total_pallets,
                'num_trucks': num_trucks,
                'agv_mode_single': 1 if agv_mode == 'single' else 0,
                'agv_mode_dual': 1 if agv_mode == 'dual' else 0,
                'agv_mode_specialized': 1 if agv_mode == 'specialized' else 0,
                'agv_capacity_tube': agv_per_hour.get('tube', 4) * 60,  # 4 AGVs * 60 min
                'agv_capacity_non_tube': agv_per_hour.get('non_tube', 3) * 60,  # 3 AGVs * 60 min
            }
            features.append(hour_features)
        
        return pd.DataFrame(features)
    
    def _statistical_forecast(self, data: pd.Series, periods: int = 12) -> List[float]:
        """Holt-Winters forecasting for time series data"""
        try:
            # Fit Holt-Winters model
            model = ExponentialSmoothing(
                data, 
                trend='add', 
                seasonal='add', 
                seasonal_periods=24  # Daily seasonality
            ).fit()
            
            # Forecast next 12 hours
            forecast = model.forecast(periods)
            return forecast.tolist()
        except:
            # Fallback to simple moving average
            return [data.mean()] * periods
    
    def _ml_forecast(self, features: pd.DataFrame) -> Dict[str, List[float]]:
        """XGBoost-based forecasting"""
        if self.xgb_model is None:
            # Train model on historical data (simplified)
            self._train_model()
        
        # Predict for each route
        predictions = {}
        routes = ['tube_station_1', 'tube_station_2', 'tube_station_3', 'tube_station_4',
                 'non_tube_station_5', 'non_tube_station_6', 'rms_a', 'rms_c']
        
        for route in routes:
            # Simplified prediction based on features
            base_volume = features['total_pallets'].iloc[0] / len(routes)
            predictions[route] = [base_volume * (1 + 0.1 * hour) for hour in range(12)]
        
        return predictions
    
    def _train_model(self):
        """Train XGBoost model on historical data"""
        # Simplified training - in real implementation, would use actual historical data
        self.xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42)
        # Training would happen here with real data
    
    def run_prediction(self, request: PredictionRequest) -> List[ForecastEntry]:
        """Main prediction method"""
        # Prepare features
        features = self._prepare_features(request)
        
        # Get statistical forecasts
        statistical_forecasts = {}
        for column in ['tube_station_1', 'tube_station_2', 'tube_station_3', 'tube_station_4',
                      'non_tube_station_5', 'non_tube_station_6', 'rms_a', 'rms_c']:
            if column in self.historical_data.columns:
                statistical_forecasts[column] = self._statistical_forecast(
                    self.historical_data[column]
                )
        
        # Get ML forecasts
        ml_forecasts = self._ml_forecast(features)
        
        # Combine forecasts (simple average)
        combined_forecasts = {}
        for route in statistical_forecasts.keys():
            stat_forecast = statistical_forecasts[route]
            ml_forecast = ml_forecasts.get(route, [0] * 12)
            
            combined = []
            for i in range(12):
                combined.append((stat_forecast[i] + ml_forecast[i]) / 2)
            combined_forecasts[route] = combined
        
        # Convert to ForecastEntry format
        forecast_entries = []
        for hour in range(12):
            for route, values in combined_forecasts.items():
                threshold = self._get_threshold(request, route, hour)
                alert = values[hour] < threshold
                
                forecast_entries.append(ForecastEntry(
                    hour=hour,
                    route=route,
                    pallet_volume=int(values[hour]),
                    threshold=threshold,
                    alert=alert
                ))
        
        return forecast_entries
    
    def _get_threshold(self, request: PredictionRequest, route: str, hour: int) -> int:
        """Get threshold for specific route and hour"""
        for threshold_config in request.thresholds:
            if threshold_config.station == route and hour < len(threshold_config.per_hour):
                return threshold_config.per_hour[hour]
        return 10  # Default threshold

# Global prediction engine instance
prediction_engine = PredictionEngine()

def run_prediction(request: PredictionRequest) -> List[ForecastEntry]:
    """Main prediction function"""
    return prediction_engine.run_prediction(request) 