/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // appDir is now default in Next.js 14
  },
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig 