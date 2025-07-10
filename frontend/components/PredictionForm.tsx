'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Calculator, Calendar, Package, Clock } from 'lucide-react'

interface PredictionFormProps {
  onPrediction: (data: any) => void
  currentShift: string
}

const PredictionForm = ({ onPrediction, currentShift }: PredictionFormProps) => {
  const [formData, setFormData] = useState({
    palletCount: 100,
    shift: currentShift,
    date: new Date().toISOString().split('T')[0],
    threshold: 15
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pallet_count: formData.palletCount,
          shift: formData.shift,
          date: formData.date
        }),
      })

      if (response.ok) {
        const data = await response.json()
        onPrediction(data)
      } else {
        console.error('Prediction failed')
      }
    } catch (error) {
      console.error('Error making prediction:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Pallet Count Input */}
      <div>
        <label className="block text-white/80 text-sm font-medium mb-2">
          <Package className="w-4 h-4 inline mr-2" />
          Pallet Count per Shift
        </label>
        <div className="relative">
          <input
            type="number"
            value={formData.palletCount}
            onChange={(e) => handleInputChange('palletCount', parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter pallet count"
            min="1"
            max="500"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50 text-sm">
            pallets
          </div>
        </div>
      </div>

      {/* Shift Selection */}
      <div>
        <label className="block text-white/80 text-sm font-medium mb-2">
          <Clock className="w-4 h-4 inline mr-2" />
          Shift Selection
        </label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { value: 'night', label: 'Night', time: '22:00-06:00' },
            { value: 'morning', label: 'Morning', time: '06:00-14:00' },
            { value: 'afternoon', label: 'Afternoon', time: '14:00-22:00' }
          ].map((shift) => (
            <motion.button
              key={shift.value}
              type="button"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleInputChange('shift', shift.value)}
              className={`p-3 rounded-lg border transition-all ${
                formData.shift === shift.value
                  ? 'bg-blue-500/30 border-blue-500/50 text-white'
                  : 'bg-white/5 border-white/20 text-white/70 hover:bg-white/10'
              }`}
            >
              <div className="text-xs font-medium">{shift.label}</div>
              <div className="text-xs opacity-70">{shift.time}</div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Date Selection */}
      <div>
        <label className="block text-white/80 text-sm font-medium mb-2">
          <Calendar className="w-4 h-4 inline mr-2" />
          Date
        </label>
        <input
          type="date"
          value={formData.date}
          onChange={(e) => handleInputChange('date', e.target.value)}
          className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Threshold Setting */}
      <div>
        <label className="block text-white/80 text-sm font-medium mb-2">
          <Calculator className="w-4 h-4 inline mr-2" />
          Threshold (Pallets/Hour)
        </label>
        <div className="relative">
          <input
            type="number"
            value={formData.threshold}
            onChange={(e) => handleInputChange('threshold', parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter threshold"
            min="1"
            max="50"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50 text-sm">
            /hour
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <motion.button
        type="submit"
        disabled={isLoading}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-3 px-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
      >
        {isLoading ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            Analyzing...
          </div>
        ) : (
          <div className="flex items-center justify-center">
            <Calculator className="w-5 h-5 mr-2" />
            Generate Prediction
          </div>
        )}
      </motion.button>

      {/* Quick Info */}
      <div className="mt-4 p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
        <h4 className="text-blue-300 font-medium text-sm mb-2">Prediction Info</h4>
        <div className="text-xs text-white/70 space-y-1">
          <p>• Expected processing time: ~{Math.round(formData.palletCount * 0.15)} minutes</p>
          <p>• Predicted efficiency: {formData.shift === 'morning' ? '95%' : formData.shift === 'afternoon' ? '90%' : '85%'}</p>
          <p>• Threshold monitoring: {formData.threshold} pallets/hour</p>
        </div>
      </div>
    </form>
  )
}

export default PredictionForm 