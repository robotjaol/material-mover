'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ForecastEntry {
  hour: number;
  route: string;
  pallet_volume: number;
  threshold: int;
  alert: boolean;
}

interface DelayEntry {
  truck_id: number;
  route: string;
  delay_minutes: number;
}

interface DashboardProps {
  forecastData?: ForecastEntry[];
  delayData?: DelayEntry[];
  alerts?: string[];
}

export default function Dashboard({ forecastData = [], delayData = [], alerts = [] }: DashboardProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [exporting, setExporting] = useState(false);

  // Group forecast data by hour for charts
  const forecastByHour = forecastData.reduce((acc, entry) => {
    if (!acc[entry.hour]) acc[entry.hour] = [];
    acc[entry.hour].push(entry);
    return acc;
  }, {} as Record<number, ForecastEntry[]>);

  // Group delay data by truck
  const delaysByTruck = delayData.reduce((acc, entry) => {
    if (!acc[entry.truck_id]) acc[entry.truck_id] = [];
    acc[entry.truck_id].push(entry);
    return acc;
  }, {} as Record<number, DelayEntry[]>);

  const handleExport = async () => {
    setExporting(true);
    try {
      // Simulate export API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Create and download CSV
      const csvContent = generateCSV();
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pallet_forecast.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExporting(false);
    }
  };

  const generateCSV = () => {
    const headers = ['Hour', 'Route', 'Pallet Volume', 'Threshold', 'Alert'];
    const rows = forecastData.map(entry => [
      entry.hour,
      entry.route,
      entry.pallet_volume,
      entry.threshold,
      entry.alert ? 'Yes' : 'No'
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  const getRouteColor = (route: string) => {
    const colors = {
      'tube_station_1': 'bg-blue-500',
      'tube_station_2': 'bg-blue-600',
      'tube_station_3': 'bg-blue-700',
      'tube_station_4': 'bg-blue-800',
      'non_tube_station_5': 'bg-green-500',
      'non_tube_station_6': 'bg-green-600',
      'rms_a': 'bg-purple-500',
      'rms_c': 'bg-purple-600'
    };
    return colors[route as keyof typeof colors] || 'bg-gray-500';
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white bg-opacity-90 backdrop-blur-sm rounded-xl shadow-lg p-6"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Live Dashboard</h2>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleExport}
          disabled={exporting}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
        >
          {exporting ? 'Exporting...' : 'Export CSV'}
        </motion.button>
      </div>

      {/* Alerts Section */}
      <AnimatePresence>
        {alerts.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6"
          >
            <h3 className="text-lg font-semibold mb-3 text-red-600">⚠️ Alerts</h3>
            <div className="space-y-2">
              {alerts.map((alert, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700"
                >
                  {alert}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Forecast Charts */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4 text-gray-700">Forecast Charts</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Hourly Forecast */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-md font-medium mb-3">Hourly Pallet Volume</h4>
            <div className="space-y-2">
              {Object.entries(forecastByHour).map(([hour, entries]) => (
                <motion.div
                  key={hour}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-2"
                >
                  <span className="text-sm font-medium w-12">H{hour}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    {entries.map((entry, index) => (
                      <motion.div
                        key={`${entry.route}-${index}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${(entry.pallet_volume / Math.max(...entries.map(e => e.pallet_volume))) * 100}%` }}
                        className={`h-full rounded-full ${getRouteColor(entry.route)} ${
                          entry.alert ? 'ring-2 ring-red-500' : ''
                        }`}
                        style={{ width: `${(entry.pallet_volume / Math.max(...entries.map(e => e.pallet_volume))) * 100}%` }}
                      />
                    ))}
                  </div>
                  <span className="text-xs text-gray-600 w-16 text-right">
                    {entries.reduce((sum, e) => sum + e.pallet_volume, 0)}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Route Comparison */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-md font-medium mb-3">Route Performance</h4>
            <div className="space-y-3">
              {Array.from(new Set(forecastData.map(f => f.route))).map(route => {
                const routeData = forecastData.filter(f => f.route === route);
                const avgVolume = routeData.reduce((sum, d) => sum + d.pallet_volume, 0) / routeData.length;
                const alerts = routeData.filter(d => d.alert).length;
                
                return (
                  <motion.div
                    key={route}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-between p-2 bg-white rounded"
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${getRouteColor(route)}`} />
                      <span className="text-sm font-medium">
                        {route.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold">{Math.round(avgVolume)}</div>
                      {alerts > 0 && (
                        <div className="text-xs text-red-600">{alerts} alerts</div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Delay Summary */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4 text-gray-700">Delay Summary</h3>
        <div className="overflow-x-auto">
          <table className="w-full bg-white rounded-lg overflow-hidden shadow">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Truck ID</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Route</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Delay (min)</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Status</th>
              </tr>
            </thead>
            <tbody>
              {delayData.map((entry, index) => (
                <motion.tr
                  key={`${entry.truck_id}-${entry.route}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border-b border-gray-200 hover:bg-gray-50"
                >
                  <td className="px-4 py-3 text-sm text-gray-900">Truck {entry.truck_id}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {entry.route.replace('_', ' ').toUpperCase()}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium">
                    {entry.delay_minutes.toFixed(1)}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      entry.delay_minutes > 30 
                        ? 'bg-red-100 text-red-800' 
                        : entry.delay_minutes > 15 
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {entry.delay_minutes > 30 ? 'High' : entry.delay_minutes > 15 ? 'Medium' : 'Low'}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-blue-50 p-4 rounded-lg"
        >
          <div className="text-2xl font-bold text-blue-600">
            {forecastData.length > 0 ? forecastData.length : 0}
          </div>
          <div className="text-sm text-blue-700">Total Forecasts</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-green-50 p-4 rounded-lg"
        >
          <div className="text-2xl font-bold text-green-600">
            {forecastData.filter(f => f.alert).length}
          </div>
          <div className="text-sm text-green-700">Threshold Alerts</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-yellow-50 p-4 rounded-lg"
        >
          <div className="text-2xl font-bold text-yellow-600">
            {delayData.length > 0 ? (delayData.reduce((sum, d) => sum + d.delay_minutes, 0) / delayData.length).toFixed(1) : 0}
          </div>
          <div className="text-sm text-yellow-700">Avg Delay (min)</div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-purple-50 p-4 rounded-lg"
        >
          <div className="text-2xl font-bold text-purple-600">
            {Array.from(new Set(delayData.map(d => d.truck_id))).length}
          </div>
          <div className="text-sm text-purple-700">Active Trucks</div>
        </motion.div>
      </div>
    </motion.div>
  );
} 