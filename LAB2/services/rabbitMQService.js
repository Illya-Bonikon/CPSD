const amqp = require("amqplib");

let channel;
const QUEUE_NAME = "meter_updates";

async function initRabbitMQ() {
	try {
		const connection = await amqp.connect("amqp://localhost");
		channel = await connection.createChannel();
		await channel.assertQueue(QUEUE_NAME, { durable: true });
		console.log("RabbitMQ з'єднано і черга створена");
	} catch (err) {
		console.error("Помилка з RabbitMQ:", err);
	}
}

function sendToQueue(data) {
	if (!channel) return;
	console.log ("data:" + Buffer.from(JSON.stringify(data)));
	channel.sendToQueue(QUEUE_NAME, Buffer.from(JSON.stringify(data)), {
		persistent: true
	});
}

module.exports = { initRabbitMQ, sendToQueue, QUEUE_NAME };
