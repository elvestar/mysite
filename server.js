import express from 'express'

const app = express()

app.use(express.static(`${__dirname}/static/build`))

app.get('/', (req, res) => {
  res.send(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>reactjs-sample</title>
      </head>
      <body>
        <div id="root"></div>
        <script src="/bundle.js"></script>
      </body>
    </html>
  `)
})

const PORT = 3000

app.listen(PORT, () => {
  console.log(`App now serving on http://localhost:${PORT}`)
})