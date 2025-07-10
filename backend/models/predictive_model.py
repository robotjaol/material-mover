import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import joblib
import os

class PredictiveModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "ml_models/pallet_predictor.pkl"
        self.scaler_path = "ml_models/scaler.pkl"
        
        # Load existing model if available
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if available"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                print("Loaded pre-trained model")
            else:
                self._train_initial_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            self._train_initial_model()
    
    def _train_initial_model(self):
        """Train initial model with synthetic data"""
        print("Training initial model with synthetic data...")
        
        # Generate synthetic training data
        X, y = self._generate_synthetic_data()
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Save model
        self._save_model()
    
    def _generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic training data"""
        np.random.seed(42)
        
        # Features: pallet_count, shift_encoded, hour, day_of_week, month
        X = np.random.rand(n_samples, 5)
        X[:, 0] = np.random.randint(50, 200, n_samples)  # pallet_count
        X[:, 1] = np.random.randint(0, 3, n_samples)      # shift (0=night, 1=morning, 2=afternoon)
        X[:, 2] = np.random.randint(0, 24, n_samples)     # hour
        X[:, 3] = np.random.randint(0, 7, n_samples)      # day_of_week
        X[:, 4] = np.random.randint(1, 13, n_samples)     # month
        
        # Target: delay_minutes (synthetic delay calculation)
        y = np.zeros(n_samples)
        for i in range(n_samples):
            pallet_count = X[i, 0]
            shift = X[i, 1]
            hour = X[i, 2]
            
            # Base delay calculation
            base_delay = pallet_count * 0.1  # 0.1 min per pallet
            
            # Shift factor
            shift_factors = {0: 1.2, 1: 0.8, 2: 1.0}  # night, morning, afternoon
            shift_factor = shift_factors.get(shift, 1.0)
            
            # Hour factor (peak hours have more delays)
            hour_factor = 1.0
            if 8 <= hour <= 12 or 14 <= hour <= 18:  # Peak hours
                hour_factor = 1.3
            
            # Random noise
            noise = np.random.normal(0, 5)
            
            y[i] = max(0, base_delay * shift_factor * hour_factor + noise)
        
        return X, y
    
    def _save_model(self):
        """Save trained model"""
        try:
            os.makedirs("ml_models", exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            print("Model saved successfully")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def predict_delay(self, pallet_count: int, shift: str, hour: int, 
                     day_of_week: int, month: int) -> Dict:
        """Predict delay for given parameters"""
        if not self.is_trained:
            self._train_initial_model()
        
        # Encode shift
        shift_encoding = {"night": 0, "morning": 1, "afternoon": 2}
        shift_encoded = shift_encoding.get(shift, 1)
        
        # Prepare features
        features = np.array([[pallet_count, shift_encoded, hour, day_of_week, month]])
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        predicted_delay = self.model.predict(features_scaled)[0]
        
        # Calculate confidence based on feature similarity to training data
        confidence = self._calculate_confidence(features_scaled[0])
        
        return {
            "predicted_delay_minutes": max(0, predicted_delay),
            "confidence": confidence,
            "features": {
                "pallet_count": pallet_count,
                "shift": shift,
                "hour": hour,
                "day_of_week": day_of_week,
                "month": month
            }
        }
    
    def _calculate_confidence(self, features_scaled):
        """Calculate prediction confidence"""
        # Simple confidence calculation based on feature ranges
        # In a real implementation, this would be more sophisticated
        confidence = 0.8  # Base confidence
        
        # Adjust based on feature values
        if features_scaled[0] < 50 or features_scaled[0] > 200:  # pallet_count
            confidence *= 0.9
        if features_scaled[2] < 6 or features_scaled[2] > 22:  # hour
            confidence *= 0.95
        
        return min(1.0, confidence)
    
    def predict_threshold_violations(self, pallet_count: int, shift: str, 
                                   threshold_pallets_per_hour: int) -> Dict:
        """Predict threshold violations"""
        # Calculate expected pallets per hour
        shift_hours = 8
        expected_pallets_per_hour = pallet_count / shift_hours
        
        # Calculate violation probability
        violation_probability = max(0, (expected_pallets_per_hour - threshold_pallets_per_hour) / threshold_pallets_per_hour)
        violation_probability = min(1.0, violation_probability)
        
        # Calculate expected delay if threshold is violated
        expected_delay = 0
        if violation_probability > 0:
            # Estimate delay based on violation severity
            violation_severity = expected_pallets_per_hour / threshold_pallets_per_hour
            expected_delay = (violation_severity - 1) * 30  # 30 min per 100% over threshold
        
        return {
            "threshold_pallets_per_hour": threshold_pallets_per_hour,
            "expected_pallets_per_hour": expected_pallets_per_hour,
            "violation_probability": violation_probability,
            "expected_delay_minutes": max(0, expected_delay),
            "status": "normal" if violation_probability < 0.1 else "warning" if violation_probability < 0.3 else "critical"
        }
    
    def get_efficiency_prediction(self, historical_data: List[Dict]) -> Dict:
        """Predict efficiency based on historical data"""
        if not historical_data:
            return {"predicted_efficiency": 0.9, "confidence": 0.7}
        
        # Calculate average efficiency from historical data
        efficiencies = [item.get("efficiency", 0.9) for item in historical_data]
        avg_efficiency = np.mean(efficiencies)
        
        # Calculate trend
        if len(efficiencies) > 1:
            trend = np.polyfit(range(len(efficiencies)), efficiencies, 1)[0]
        else:
            trend = 0
        
        # Predict future efficiency
        predicted_efficiency = avg_efficiency + trend * 0.1  # Small trend adjustment
        predicted_efficiency = max(0.5, min(1.0, predicted_efficiency))  # Clamp between 0.5 and 1.0
        
        return {
            "predicted_efficiency": predicted_efficiency,
            "historical_average": avg_efficiency,
            "trend": trend,
            "confidence": min(0.9, 0.7 + len(historical_data) * 0.02)  # More data = higher confidence
        }
    
    def update_model(self, new_data: List[Dict]):
        """Update model with new data"""
        if not new_data:
            return
        
        # Extract features and targets from new data
        X_new = []
        y_new = []
        
        for item in new_data:
            features = item.get("features", {})
            if features:
                X_new.append([
                    features.get("pallet_count", 0),
                    features.get("shift_encoded", 1),
                    features.get("hour", 12),
                    features.get("day_of_week", 0),
                    features.get("month", 1)
                ])
                y_new.append(item.get("actual_delay_minutes", 0))
        
        if X_new and y_new:
            X_new = np.array(X_new)
            y_new = np.array(y_new)
            
            # Retrain model with new data
            X_combined = np.vstack([self.scaler.inverse_transform(self.scaler.transform(X_new)), X_new])
            y_combined = np.concatenate([y_new, y_new])  # Simplified - in practice, you'd have historical targets
            
            self.model.fit(X_combined, y_combined)
            self._save_model()
            
            print(f"Model updated with {len(new_data)} new data points") 