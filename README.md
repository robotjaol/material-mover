# Real-Time Predictive Pallet Flow Diagnostic and Delay Estimation Platform for Smart Factory Distribution Networks

## Project Overview
A full-stack, modular, real-time platform to predict and visualize pallet distribution and delays in smart factory networks. Computes predictive pallet flow, estimates delays, detects bottlenecks, and visualizes results in a live dashboard.

## System Architecture
- **Backend**: FastAPI (Python), ML/statistical models, REST API
- **Frontend**: Next.js (React), TailwindCSS, Framer Motion, animated/3D backgrounds
- **Data**: User input + historical, real-time simulation

## Data Flow
```
User Input (UI)
   ↓
Real-Time Config Dispatch → Backend
   ↓
Prediction Engine → Forecast + Delay Estimator
   ↓
API Response → Frontend Rendered Charts + Tables
   ↓
Optional Export (CSV) / Alerts
```

## ML Pipeline
- Preprocessing: Normalization, smoothing, time alignment
- Forecasting: Holt-Winters, ARIMA/SARIMA
- ML: XGBoost Regression
- Delay: Custom AGV queuing logic

## UI Component Map
- Config Form: Truck, pallet, AGV, thresholds, material type, AGV mode
- Dashboard: Forecast charts, delay tables, alerts, export button
- Animated Background: Particle spheres/3D

## API Specification

### POST /predict
**Request Body:**
```json
{
  "trucks": [
    {
      "truck_id": 1,
      "pallet_volume": 20,
      "arrival_time": "08:00"
    }
  ],
  "agv_config": {
    "mode": "single",
    "per_hour": {
      "tube": 4,
      "non_tube": 3
    }
  },
  "thresholds": [
    {
      "station": "tube_station_1",
      "per_hour": [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
    }
  ],
  "material_assignments": {
    "tube": "tube",
    "non_tube": "non_tube"
  }
}
```

**Response:**
```json
{
  "forecast_table": [
    {
      "hour": 0,
      "route": "tube_station_1",
      "pallet_volume": 15,
      "threshold": 15,
      "alert": false
    }
  ],
  "delay_summary": [
    {
      "truck_id": 1,
      "route": "tube_station_1",
      "delay_minutes": 5.2
    }
  ],
  "alerts": [
    "⚠️ Threshold breaches detected: Route tube_station_1 at hour 0: 15 pallets (threshold: 15)"
  ]
}
```

### POST /export
Exports forecast and delay data as CSV file.

## Backend Structure
- `main.py`: FastAPI entry
- `api/`: Routes
- `models/`: Pydantic schemas, ML models
- `services/`: Prediction, analytics, delay
- `utils/`: Helpers
- `ml_models/`: Trained models

## Deployment

### Local Development

1. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Start Development Servers**
   ```bash
   # Option 1: Use startup script
   ./start.sh
   
   # Option 2: Start manually
   # Terminal 1 - Backend
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Deployment

#### Backend (FastAPI)
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend (Next.js)
```bash
# Build for production
npm run build

# Start production server
npm start
```

#### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment (Vercel)
1. Connect repository to Vercel
2. Configure build settings for Next.js
3. Set environment variables for API endpoints
4. Deploy

## Sample Data
Sample historical data is provided in `data/sample_data.json` for testing and development.

## Features Implemented

### ✅ Backend
- [x] FastAPI REST API with CORS
- [x] Prediction engine (Holt-Winters + XGBoost)
- [x] Delay estimation with AGV queuing logic
- [x] Threshold alerting system
- [x] CSV export functionality
- [x] Pydantic schema validation

### ✅ Frontend
- [x] Interactive configuration form
- [x] Real-time dashboard with charts
- [x] Animated background (Three.js particles)
- [x] Framer Motion animations
- [x] Responsive design (mobile/desktop)
- [x] CSV export functionality
- [x] Error handling and loading states

### ✅ Integration
- [x] Frontend-backend API communication
- [x] Real-time data updates
- [x] Alert system integration
- [x] Export functionality

## Future Work
- Real AGV integration
- Advanced ML models (LSTM, Transformer)
- More visualization types (3D maps, heatmaps)
- Multi-factory support
- Real-time data streaming
- Advanced analytics and reporting
- Mobile app development
- Integration with ERP systems

## Technology Stack
- **Backend**: Python, FastAPI, pandas, numpy, statsmodels, scikit-learn, xgboost
- **Frontend**: Next.js, React, TypeScript, TailwindCSS, Framer Motion, Three.js
- **Deployment**: Docker, Vercel, cloud-ready

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License
MIT License - see LICENSE file for details 