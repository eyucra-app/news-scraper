import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Static export para Vercel (sin SSR)
  output: 'export',
  
  // Deshabilitar optimización de imágenes para static export
  images: {
    unoptimized: true,
  },
  
  // Variables de entorno
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },
  
  // Trailing slashes para mejor compatibilidad
  trailingSlash: true,
};

export default nextConfig;
