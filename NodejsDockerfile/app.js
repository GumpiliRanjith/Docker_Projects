const express = require("express");

const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Express running inside Docker! 🐳");
});

app.listen(3000, "0.0.0.0", () => {
  console.log("Express server is running on port 3000");
});
