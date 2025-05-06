const Meter = require("../models/meterModel");

const meters = [
	{
		meterId: "test1",
		previousDayReading: 0,
		previousNightReading: 0,
		currentDayReading: 10,
		currentNightReading: 5,
		totalAmount: 0,
		date: new Date(),
	},
	{
		meterId: "test2",
		previousDayReading: 0,
		previousNightReading: 0,
		currentDayReading: 20,
		currentNightReading: 10,
		totalAmount: 0,
		date: new Date(),
	},
];

async function seedMeters() {
	try {

		const existingMeters = await Meter.countDocuments();
		if (existingMeters > 0) 	return;
		
		await Meter.insertMany(meters);
	} catch (error) {
		console.error("Помилка додавання записів лічильників:", error);
	}
}

module.exports = { seedMeters };