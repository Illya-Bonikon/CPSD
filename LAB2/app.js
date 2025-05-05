const express = require("express");
const path = require("path");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const meterRoutes = require("./routes/meterRoutes");
const { seedMeters } = require("./seeders/seedMeters");
const { seedTariff } = require("./seeders/seedTariffs");

const app = express();
const PORT = 5000;

mongoose.connect("mongodb://localhost:27017/metersDB")
.then(() => {
	console.log("Успішно підключено до MongoDB");

	seedMeters();
	seedTariff();

	app.listen(PORT, () => {
		console.log(`Server is running on http://localhost:${PORT}`);
	});
})
.catch((error) => {
	console.error("Виникла проблема під час підключення до MongoDB: ", error);
	process.exit(1);
});

  
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "public")));
app.use("/api/meters", meterRoutes);



