const express = require("express");
const path = require("path");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const meterRoutes = require("./routes/meterRoutes");
const { seedMeters } = require("./seeders/seedMeters");
const { seedTariff } = require("./seeders/seedTariffs");
const { initRabbitMQ } = require("./services/rabbitMQService");	

const app = express();
const PORT = 5000;

mongoose.connect("mongodb://localhost:27017/metersDB")
	.then(async () => {
		console.log("Успішно підключено до MongoDB");

		try {
			await seedTariff();
			await seedMeters();
			await initRabbitMQ();

		} catch (error) {
			console.error("Помилка під час задання тестовиз значень:", error);
		}
		
		app.listen(PORT, () => {
		console.log(`Сервер працює на http://localhost:${PORT}`);
		});
	})
	.catch((error) => {
		console.error("Проблема з підключенням до MongoDB: ", error);
		process.exit(1);
	});

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "public")));

app.use("/api/meters", meterRoutes);

process.on('SIGINT', async () => {
	await mongoose.connection.close();
	console.log('MongoDB з\'єднання закрито');
	process.exit(0);
});
