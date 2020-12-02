const express = require('express')
const path = require('path');
const app = express()
const port = 3000

const tenantname = process.env.tenantname
const tenant = process.env.tenant
const api = process.env.api

app.engine('.html', require('ejs').__express);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'html');

app.get('/', (req, res) => {
  res.render('index', {
    title: tenantname,
    tenantid: tenant,
    apiaddress: api
  }); 
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})