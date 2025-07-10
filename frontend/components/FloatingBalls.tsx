'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

const FloatingBalls = () => {
  const ballsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const balls = ballsRef.current
    if (!balls) return

    const createBall = () => {
      const ball = document.createElement('div')
      ball.className = 'absolute rounded-full opacity-20'
      ball.style.width = `${Math.random() * 60 + 20}px`
      ball.style.height = ball.style.width
      ball.style.left = `${Math.random() * 100}%`
      ball.style.top = `${Math.random() * 100}%`
      ball.style.background = `hsl(${Math.random() * 360}, 70%, 60%)`
      ball.style.animation = `float ${Math.random() * 10 + 10}s ease-in-out infinite`
      ball.style.animationDelay = `${Math.random() * 5}s`
      
      balls.appendChild(ball)

      // Remove ball after animation
      setTimeout(() => {
        if (ball.parentNode) {
          ball.parentNode.removeChild(ball)
        }
      }, 15000)
    }

    // Create initial balls
    for (let i = 0; i < 15; i++) {
      setTimeout(createBall, i * 1000)
    }

    // Continue creating balls
    const interval = setInterval(createBall, 2000)

    return () => {
      clearInterval(interval)
      if (balls) {
        balls.innerHTML = ''
      }
    }
  }, [])

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      <div ref={ballsRef} className="relative w-full h-full" />
      
      {/* Static gradient orbs */}
      <motion.div
        className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full opacity-10"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.1, 0.2, 0.1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      <motion.div
        className="absolute top-40 right-32 w-24 h-24 bg-gradient-to-r from-green-400 to-blue-400 rounded-full opacity-10"
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.1, 0.15, 0.1],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      <motion.div
        className="absolute bottom-32 left-1/3 w-40 h-40 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full opacity-10"
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.1, 0.25, 0.1],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      <motion.div
        className="absolute bottom-20 right-20 w-28 h-28 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full opacity-10"
        animate={{
          scale: [1, 1.4, 1],
          opacity: [0.1, 0.2, 0.1],
        }}
        transition={{
          duration: 7,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </div>
  )
}

export default FloatingBalls 