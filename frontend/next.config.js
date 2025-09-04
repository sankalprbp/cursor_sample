/** @type {import('next').NextConfig} */
const isDevelopment = process.env.NODE_ENV === 'development'
const isProduction = process.env.NODE_ENV === 'production'

const nextConfig = {
  // Use standalone output for production Docker builds
  output: isProduction ? 'standalone' : undefined,
  
  // Image optimization configuration
  images: {
    domains: ['localhost'],
    // Add production domains when available
    ...(isProduction && {
      domains: ['localhost', process.env.NEXT_PUBLIC_DOMAIN].filter(Boolean)
    })
  },
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // TypeScript configuration - only ignore errors in development for rapid prototyping
  typescript: {
    ignoreBuildErrors: isDevelopment,
  },
  
  // ESLint configuration - only ignore in development
  eslint: {
    ignoreDuringBuilds: isDevelopment,
    // In production, fail the build on ESLint errors
    ...(isProduction && {
      dirs: ['src']
    })
  },
  
  // Performance optimizations
  experimental: {
    // Enable modern bundling optimizations
    optimizeCss: true,
    // Reduce bundle size
    optimizePackageImports: ['@heroicons/react']
  },
  
  // Security headers for production
  ...(isProduction && {
    async headers() {
      return [
        {
          source: '/(.*)',
          headers: [
            {
              key: 'X-Frame-Options',
              value: 'DENY'
            },
            {
              key: 'X-Content-Type-Options',
              value: 'nosniff'
            },
            {
              key: 'Referrer-Policy',
              value: 'origin-when-cross-origin'
            }
          ]
        }
      ]
    }
  }),
  
  // Webpack configuration for better error handling
  webpack: (config, { dev, isServer }) => {
    // Better error reporting in development
    if (dev) {
      config.devtool = 'eval-source-map'
    }
    
    // Optimize bundle size
    if (!dev && !isServer) {
      config.optimization.splitChunks.cacheGroups = {
        ...config.optimization.splitChunks.cacheGroups,
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        }
      }
    }
    
    return config
  }
}

module.exports = nextConfig