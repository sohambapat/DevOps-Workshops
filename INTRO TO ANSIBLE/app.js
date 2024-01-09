// app.js
const http = require('http');

const hostname = '0.0.0.0';
const port = 80;

//const server = http.createServer((req, res) => {
 // res.statusCode = 200;
//  res.setHeader('Content-Type', 'text/plain');
//  res.end('Hello CSC-519 World!\n');
//});

http.createServer(function (request, response) {
   // Send the HTTP header 
   // HTTP Status: 200 : OK
   // Content Type: text/plain
   response.writeHead(200, {'Content-Type': 'text/plain'});
   
   // Send the response body as "Hello World"
   response.end('Hello World\n');
}).listen(80);

console.log("Server running at http://${hostname}:${port}/");
