const express = require('express')

const app = express()
const port = 8000

app.get('/test', (req, res) => res.send('Hello! This is the FAMNM Backend.'))

app.listen(port, () => console.log(`app listening at https:\/\/localhost:${port}!`))

