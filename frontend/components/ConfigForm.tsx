'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface TruckConfig {
  truck_id: number;
  pallet_volume: number;
  arrival_time: string;
}

interface AGVConfig {
  mode: string;
  per_hour: {
    tube: number;
    non_tube: number;
  };
}

interface ThresholdConfig {
  station: string;
  per_hour: number[];
}

interface ConfigFormProps {
  onConfigChange: (config: any) => void;
}

export default function ConfigForm({ onConfigChange }: ConfigFormProps) {
  const [trucks, setTrucks] = useState<TruckConfig[]>([
    { truck_id: 1, pallet_volume: 20, arrival_time: '08:00' }
  ]);
  
  const [agvConfig, setAgvConfig] = useState<AGVConfig>({
    mode: 'single',
    per_hour: { tube: 4, non_tube: 3 }
  });
  
  const [thresholds, setThresholds] = useState<ThresholdConfig[]>([
    { station: 'tube_station_1', per_hour: Array(12).fill(15) },
    { station: 'tube_station_2', per_hour: Array(12).fill(12) },
    { station: 'tube_station_3', per_hour: Array(12).fill(10) },
    { station: 'tube_station_4', per_hour: Array(12).fill(8) },
    { station: 'non_tube_station_5', per_hour: Array(12).fill(20) },
    { station: 'non_tube_station_6', per_hour: Array(12).fill(18) },
    { station: 'rms_a', per_hour: Array(12).fill(45) },
    { station: 'rms_c', per_hour: Array(12).fill(38) }
  ]);
  
  const [materialAssignments, setMaterialAssignments] = useState({
    'tube': 'tube',
    'non_tube': 'non_tube'
  });

  const addTruck = () => {
    const newTruckId = trucks.length + 1;
    setTrucks([...trucks, { 
      truck_id: newTruckId, 
      pallet_volume: 20, 
      arrival_time: '08:00' 
    }]);
  };

  const removeTruck = (index: number) => {
    if (trucks.length > 1) {
      setTrucks(trucks.filter((_, i) => i !== index));
    }
  };

  const updateTruck = (index: number, field: keyof TruckConfig, value: any) => {
    const updatedTrucks = [...trucks];
    updatedTrucks[index] = { ...updatedTrucks[index], [field]: value };
    setTrucks(updatedTrucks);
  };

  const updateThreshold = (stationIndex: number, hourIndex: number, value: number) => {
    const updatedThresholds = [...thresholds];
    updatedThresholds[stationIndex].per_hour[hourIndex] = value;
    setThresholds(updatedThresholds);
  };

  const handleSubmit = () => {
    const config = {
      trucks,
      agv_config: agvConfig,
      thresholds,
      material_assignments: materialAssignments
    };
    onConfigChange(config);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white bg-opacity-90 backdrop-blur-sm rounded-xl shadow-lg p-6 mb-6"
    >
      <h2 className="text-2xl font-bold mb-6 text-gray-800">System Configuration</h2>
      
      {/* Truck Configuration */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-700">Truck Configuration</h3>
        <div className="space-y-3">
          {trucks.map((truck, index) => (
            <motion.div 
              key={truck.truck_id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-4 items-center p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-600">Truck {truck.truck_id}</label>
                <div className="grid grid-cols-2 gap-4 mt-2">
                  <div>
                    <label className="block text-xs text-gray-500">Pallet Volume</label>
                    <input
                      type="number"
                      value={truck.pallet_volume}
                      onChange={(e) => updateTruck(index, 'pallet_volume', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500">Arrival Time</label>
                    <input
                      type="time"
                      value={truck.arrival_time}
                      onChange={(e) => updateTruck(index, 'arrival_time', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
              {trucks.length > 1 && (
                <button
                  onClick={() => removeTruck(index)}
                  className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
                >
                  Remove
                </button>
              )}
            </motion.div>
          ))}
          <button
            onClick={addTruck}
            className="w-full py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Add Truck
          </button>
        </div>
      </div>

      {/* AGV Configuration */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-700">AGV Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">AGV Mode</label>
            <select
              value={agvConfig.mode}
              onChange={(e) => setAgvConfig({...agvConfig, mode: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="single">Single AGV</option>
              <option value="dual">Dual AGV</option>
              <option value="specialized">AGV 1 khusus material A / AGV 2 khusus material B</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">AGV Capacity per Hour</label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-gray-500">Tube AGVs</label>
                <input
                  type="number"
                  value={agvConfig.per_hour.tube}
                  onChange={(e) => setAgvConfig({
                    ...agvConfig, 
                    per_hour: {...agvConfig.per_hour, tube: parseInt(e.target.value)}
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500">Non-Tube AGVs</label>
                <input
                  type="number"
                  value={agvConfig.per_hour.non_tube}
                  onChange={(e) => setAgvConfig({
                    ...agvConfig, 
                    per_hour: {...agvConfig.per_hour, non_tube: parseInt(e.target.value)}
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Material Assignment */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-700">Material Assignment</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">Tube Material</label>
            <select
              value={materialAssignments.tube}
              onChange={(e) => setMaterialAssignments({...materialAssignments, tube: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="tube">Tube-type pallets</option>
              <option value="non_tube">Non-Tube-type pallets</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">Non-Tube Material</label>
            <select
              value={materialAssignments.non_tube}
              onChange={(e) => setMaterialAssignments({...materialAssignments, non_tube: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="non_tube">Non-Tube-type pallets</option>
              <option value="tube">Tube-type pallets</option>
            </select>
          </div>
        </div>
      </div>

      {/* Thresholds */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-700">Threshold Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {thresholds.map((threshold, stationIndex) => (
            <div key={threshold.station} className="p-3 bg-gray-50 rounded-lg">
              <label className="block text-sm font-medium text-gray-600 mb-2">
                {threshold.station.replace('_', ' ').toUpperCase()}
              </label>
              <div className="space-y-1">
                {threshold.per_hour.slice(0, 6).map((value, hourIndex) => (
                  <div key={hourIndex} className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 w-8">H{hourIndex}</span>
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => updateThreshold(stationIndex, hourIndex, parseInt(e.target.value))}
                      className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleSubmit}
        className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
      >
        Generate Prediction
      </motion.button>
    </motion.div>
  );
} 