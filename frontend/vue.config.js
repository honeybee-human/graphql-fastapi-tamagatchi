module.exports = {
  outputDir: 'dist',
  publicPath: '/',
  devServer: {
    port: 3000,
    proxy: {
      '/graphql': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}