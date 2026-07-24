/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Fetch updates.json from GitHub raw content
  async redirects() {
    return [];
  },
};

module.exports = nextConfig;
