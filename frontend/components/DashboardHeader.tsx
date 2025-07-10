'use client'

import { motion } from 'framer-motion'
import { Clock, Activity, Settings, Bell } from 'lucide-react'

interface DashboardHeaderProps {
  currentShift: string
}

const DashboardHeader = ({ currentShift }: DashboardHeaderProps) => {
  const getShiftInfo = (shift: string) => {
    switch (shift) {
      case 'night':
        return {
          name: 'Night Shift',
          time: '22:00 - 06:00',
          color: 'from-purple-500 to-indigo-600',
          icon: '🌙'
        }
      case 'morning':
        return {
          name: 'Morning Shift',
          time: '06:00 - 14:00',
          color: 'from-blue-500 to-cyan-600',
          icon: '🌅'
        }
      case 'afternoon':
        return {
          name: 'Afternoon Shift',
          time: '14:00 - 22:00',
          color: 'from-orange-500 to-red-600',
          icon: '🌆'
        }
      default:
        return {
          name: 'Unknown Shift',
          time: '--:-- - --:--',
          color: 'from-gray-500 to-gray-600',
          icon: '❓'
        }
    }
  }

  const shiftInfo = getShiftInfo(currentShift)

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="glass-card border-b border-white/10"
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          {/* Left side - Title and Shift */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
                <Activity className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  Smart Factory Diagnostics
                </h1>
                <p className="text-blue-200 text-sm">
                  Predictive Pallet Movement Analytics
                </p>
              </div>
            </div>

            {/* Current Shift Badge */}
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3 }}
              className={`px-4 py-2 rounded-full bg-gradient-to-r ${shiftInfo.color} text-white flex items-center gap-2`}
            >
              <span className="text-lg">{shiftInfo.icon}</span>
              <div>
                <p className="font-semibold text-sm">{shiftInfo.name}</p>
                <p className="text-xs opacity-90">{shiftInfo.time}</p>
              </div>
            </motion.div>
          </div>

          {/* Right side - Status and Actions */}
          <div className="flex items-center gap-4">
            {/* System Status */}
            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 rounded-lg border border-green-500/30">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-green-400 text-sm font-medium">System Online</span>
            </div>

            {/* Current Time */}
            <div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg">
              <Clock className="w-4 h-4 text-blue-300" />
              <span className="text-white text-sm">
                {new Date().toLocaleTimeString()}
              </span>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
              >
                <Bell className="w-5 h-5 text-white" />
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
              >
                <Settings className="w-5 h-5 text-white" />
              </motion.button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 1, delay: 0.5 }}
          className="mt-4 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full"
        />
      </div>
    </motion.header>
  )
}

export default DashboardHeader 