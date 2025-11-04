import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // Для Tauri важно отключить строгий режим в production
  distDir: 'out',
};

export default nextConfig;
