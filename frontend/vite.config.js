import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  server: {
    // 0.0.0.0 allows the container to be accessed externally (by the Ingress)
    host: '0.0.0.0', 
    
    // Explicitly allow 'hori.local' requests from the browser
    allowedHosts: ['hori.local'],
    
    // Fixes issues where HMR (live reloading) breaks in Docker/Kubernetes
    hmr: {
      clientPort: 5173, // Use the service port
      host: 'hori.local', // Use the external host name for HMR
      protocol: 'ws' 
    }
  }
});