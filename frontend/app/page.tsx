'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Activity, 
  Clock, 
  TrendingUp, 
  AlertTriangle, 
  Factory, 
  Package,
  BarChart3,
  Settings,
  Zap
} from 'lucide-react'
import DashboardHeader from '@/components/DashboardHeader'
import MetricsCards from '@/components/MetricsCards'
import PredictionForm from '@/components/PredictionForm'
import ThreeDVisualization from '@/components/ThreeDVisualization'
import AnalyticsCharts from '@/components/AnalyticsCharts'
import RealtimeStatus from '@/components/RealtimeStatus'
import FloatingBalls from '@/components/FloatingBalls'

export default function Dashboard() {
  const [currentShift, setCurrentShift] = useState('morning')
  const [realtimeData, setRealtimeData] = useState(null)
  const [predictionData, setPredictionData] = useState(null)

  useEffect(() => {
    // Determine current shift based on time
    const hour = new Date().getHours()
    if (hour >= 22 || hour < 6) setCurrentShift('night')
    else if (hour >= 6 && hour < 14) setCurrentShift('morning')
    else setCurrentShift('afternoon')

    // Fetch real-time data
    fetchRealtimeData()
    const interval = setInterval(fetchRealtimeData, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const fetchRealtimeData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/realtime')
      const data = await response.json()
      setRealtimeData(data)
    } catch (error) {
      console.error('Error fetching real-time data:', error)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <FloatingBalls />
      
      {/* Main Content */}
      <div className="relative z-10">
        <DashboardHeader currentShift={currentShift} />
        
        <div className="container mx-auto px-4 py-8">
          {/* Metrics Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <MetricsCards realtimeData={realtimeData} />
          </motion.div>

          {/* Main Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
            {/* Left Column - Prediction Form & Analytics */}
            <div className="lg:col-span-1 space-y-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="glass-card p-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-blue-500/20 rounded-lg">
                      <Zap className="w-6 h-6 text-blue-400" />
                    </div>
                    <h2 className="text-xl font-semibold text-white">Predictive Analysis</h2>
                  </div>
                  <PredictionForm 
                    onPrediction={setPredictionData}
                    currentShift={currentShift}
                  />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <div className="glass-card p-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-green-500/20 rounded-lg">
                      <BarChart3 className="w-6 h-6 text-green-400" />
                    </div>
                    <h2 className="text-xl font-semibold text-white">Analytics</h2>
                  </div>
                  <AnalyticsCharts shift={currentShift} />
                </div>
              </motion.div>
            </div>

            {/* Center Column - 3D Visualization */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="lg:col-span-1"
            >
              <div className="glass-card p-6 h-full">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-purple-500/20 rounded-lg">
                    <Factory className="w-6 h-6 text-purple-400" />
                  </div>
                  <h2 className="text-xl font-semibold text-white">3D Factory View</h2>
                </div>
                <div className="h-96">
                  <ThreeDVisualization predictionData={predictionData} />
                </div>
              </div>
            </motion.div>

            {/* Right Column - Real-time Status */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="lg:col-span-1"
            >
              <div className="glass-card p-6 h-full">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-orange-500/20 rounded-lg">
                    <Activity className="w-6 h-6 text-orange-400" />
                  </div>
                  <h2 className="text-xl font-semibold text-white">Real-time Status</h2>
                </div>
                <RealtimeStatus data={realtimeData} />
              </div>
            </motion.div>
          </div>

          {/* Bottom Section - Detailed Charts */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mt-8"
          >
            <div className="glass-card p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-indigo-500/20 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-indigo-400" />
                </div>
                <h2 className="text-xl font-semibold text-white">Performance Trends</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="h-64">
                  <AnalyticsCharts shift={currentShift} type="efficiency" />
                </div>
                <div className="h-64">
                  <AnalyticsCharts shift={currentShift} type="delays" />
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
} 