import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react({
    jsxRuntime: 'automatic',
    babel: {
      plugins: mode === 'production' ? [
        ['babel-plugin-react-remove-properties', { properties: ['data-testid'] }]
      ] : []
    }
  })],
  
  server: {
    port: 5174,
    host: true,
    open: false
  },

  build: {
    outDir: 'dist',
    sourcemap: false,
    target: 'es2020',
    minify: 'terser',
    cssMinify: true,
    
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Core React
          if (id.includes('react') || id.includes('react-dom')) {
            return 'react-vendor';
          }
          
          // Router
          if (id.includes('react-router')) {
            return 'react-router';
          }
          
          // Charts optimization - hanya recharts
          if (id.includes('recharts')) {
            return 'charts-recharts';
          }
          
          // Data fetching
          if (id.includes('@tanstack/react-query') || id.includes('axios')) {
            return 'data-vendor';
          }
          
          // Utilities
          if (id.includes('dayjs') || id.includes('clsx') || id.includes('tailwind-merge')) {
            return 'utils-vendor';
          }
          
          // Node modules default
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        },
        
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? 
            chunkInfo.facadeModuleId.split('/').pop() : 'chunk';
          return `js/${facadeModuleId}-[hash].js`;
        },
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith('.css')) {
            return 'assets/[name]-[hash].[ext]';
          }
          return 'assets/[name]-[hash].[ext]';
        }
      }
    },
    
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn'],
        reduce_vars: true,
        reduce_funcs: true,
      },
      mangle: {
        safari10: true,
      },
      format: {
        comments: false,
      }
    },
    
    // Performance optimizations
    reportCompressedSize: false,
    chunkSizeWarningLimit: 1000,
    assetsInlineLimit: 4096, // Inline small assets
  },

  optimizeDeps: {
    include: [
      'react', 
      'react-dom', 
      'react-router-dom', 
      'axios',
      '@tanstack/react-query',
      'dayjs',
      'clsx',
      'tailwind-merge'
    ],
    exclude: ['chart.js', 'recharts'] // Lazy load charts
  },

  css: {
    devSourcemap: false,
    postcss: {
      plugins: mode === 'production' ? [
        require('autoprefixer'),
        require('cssnano')({
          preset: 'default'
        })
      ] : [require('autoprefixer')]
    }
  },

  // Preview server config
  preview: {
    port: 4173,
    host: true,
    headers: {
      'Cache-Control': 'max-age=31536000, immutable'
    }
  }
}))
