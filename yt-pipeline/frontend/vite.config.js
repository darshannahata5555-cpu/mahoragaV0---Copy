import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // All /api calls are forwarded to FastAPI — avoids CORS issues in dev
      '/api': 'http://localhost:8000',
    },
  },
})
