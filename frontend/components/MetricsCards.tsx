'use client'

import { motion } from 'framer-motion'
import { Package, Clock, TrendingUp, AlertTriangle, Activity, Zap } from 'lucide-react'

interface MetricsCardsProps {
  realtimeData: any
}

const MetricsCards = ({ realtimeData }: MetricsCardsProps) => {
  const metrics = [
    {
      title: 'Active Pallets',
      value: realtimeData?.active_pallets || 0,
      change: '+12%',
      icon: Package,
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-500/20',
      borderColor: 'border-blue-500/30'
    },
    {
      title: 'System Efficiency',
      value: `${((realtimeData?.efficiency || 0.9) * 100).toFixed(1)}%`,
      change: '+2.3%',
      icon: TrendingUp,
      color: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-500/20',
      borderColor: 'border-green-500/30'
    },
    {
      title: 'Processing Time',
      value: '15.2 min',
      change: '-8.5%',
      icon: Clock,
      color: 'from-purple-500 to-pink-500',
      bgColor: 'bg-purple-500/20',
      borderColor: 'border-purple-500/30'
    },
    {
      title: 'Active Alerts',
      value: realtimeData?.alerts?.length || 0,
      change: '-3',
      icon: AlertTriangle,
      color: 'from-orange-500 to-red-500',
      bgColor: 'bg-orange-500/20',
      borderColor: 'border-orange-500/30'
    },
    {
      title: 'Stations Online',
      value: '9/9',
      change: '100%',
      icon: Activity,
      color: 'from-indigo-500 to-blue-500',
      bgColor: 'bg-indigo-500/20',
      borderColor: 'border-indigo-500/30'
    },
    {
      title: 'Power Status',
      value: 'Optimal',
      change: 'Normal',
      icon: Zap,
      color: 'from-yellow-500 to-orange-500',
      bgColor: 'bg-yellow-500/20',
      borderColor: 'border-yellow-500/30'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {metrics.map((metric, index) => (
        <motion.div
          key={metric.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
          className={`glass-card p-6 border ${metric.borderColor} hover:scale-105 transition-transform duration-300`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/70 text-sm font-medium">{metric.title}</p>
              <p className="text-2xl font-bold text-white mt-2">{metric.value}</p>
              <p className="text-xs text-green-400 mt-1">{metric.change}</p>
            </div>
            
            <div className={`p-3 rounded-xl bg-gradient-to-r ${metric.color} ${metric.bgColor}`}>
              <metric.icon className="w-6 h-6 text-white" />
            </div>
          </div>

          {/* Progress indicator */}
          <div className="mt-4">
            <div className="flex justify-between text-xs text-white/60 mb-1">
              <span>Performance</span>
              <span>100%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: '85%' }}
                transition={{ duration: 1, delay: index * 0.1 + 0.5 }}
                className={`h-2 rounded-full bg-gradient-to-r ${metric.color}`}
              />
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  )
}

export default MetricsCards 