module.exports = {
  outputDir: 'dist',
  publicPath: '/',
  css: {
    loaderOptions: {
      // Ensure sass-loader uses Dart Sass implementation for both .sass and .scss
      sass: {
        implementation: require('sass'),
        // Instruct sass-loader to use the modern Sass JS API
        api: 'modern',
        // Silence legacy deprecation warnings in case any upstream still hits legacy API
        sassOptions: {
          silenceDeprecations: ['legacy-js-api'],
        },
      },
      scss: {
        implementation: require('sass'),
        api: 'modern',
        sassOptions: {
          silenceDeprecations: ['legacy-js-api'],
        },
      },
    },
  },
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