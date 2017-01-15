export default {
  entry: './src/index.js',
  output: {
    filename: './node_modules/build/bundle.js'
  },
  module: {
    loaders: [{
      test: /\.js[x]?$/,
      exclude: /node_modules/,
      loader: 'babel'
    }, {
      test: /\.scss$/,
      // include: /src/,
      exclude: /node_modules/,
      loader: 'style!css!sass'
    }]
  }
}
