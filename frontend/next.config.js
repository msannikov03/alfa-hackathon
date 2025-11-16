/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:8000/api/:path*'
      },
      {
        source: '/ws',
        destination: 'http://backend:8000/ws'
      }
    ]
  }
}

module.exports = nextConfig
