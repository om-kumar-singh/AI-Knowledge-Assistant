import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // When multiple lockfiles exist above this app, pin Turbopack to the frontend directory.
    root: process.cwd(),
  },
};

export default nextConfig;
