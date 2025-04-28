const express = require("express");
const path = require("path");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const meterRoutes = require("./routes/meterRoutes");

const app = express();
const PORT = 5000;

mongoose.connect("mongodb://localhost:27017/metersDB", {
useNewUrlParser: true,
useUnifiedTopology: true,
})
.then(() => console.log("Успішно підключено до MongoDB"))
.catch((error) => console.error("Виникла проблема під час підключення до MongoDB: ", error));

  
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "public")));
app.use("/api/meters", meterRoutes);


app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
