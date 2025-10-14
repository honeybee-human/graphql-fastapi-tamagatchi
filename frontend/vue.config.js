module.exports = {
  outputDir: 'dist',
  publicPath: '/',
  devServer: {
    port: 3000,
    proxy: {
      // Allow overriding backend target for Docker compose via env
      '/graphql': {
        target: process.env.BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: process.env.BACKEND_URL || 'http://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
}