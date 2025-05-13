const Meter = require("../models/meterModel");
const Tariff = require("../models/tariffModel");
const { sendToQueue } = require("./rabbitMQService");

async function calculateBill(prevDay, prevNight, currDay, currNight, tariff) {
	const day = (currDay - prevDay) * tariff.dayRate;
	const night = (currNight - prevNight) * tariff.nightRate;
	return day + night;
}

async function addMeterData(meterId, newDay, newNight) {
	const tariff = await Tariff.findOne();
	if (!tariff) return { error: "Тариф не знайдено" };

	const last = await Meter.findOne({ meterId }).sort({ date: -1 });
	if (!last) return { error: "Лічильник не знайдено" };

	if (newDay < last.currentDayReading)			newDay = last.currentDayReading + tariff.dayOverflow;
	if (newNight < last.currentNightReading)		newNight = last.currentNightReading + tariff.nightOverflow;

	const totalAmount = await calculateBill(
		last.currentDayReading,
		last.currentNightReading,
		newDay,
		newNight,
		tariff
	);

	const newRecord = new Meter({
		meterId,
		previousDayReading: last.currentDayReading,
		previousNightReading: last.currentNightReading,
		currentDayReading: newDay,
		currentNightReading: newNight,
		totalAmount,
		date: new Date()
	});	

	await newRecord.save();
	sendToQueue({ meterId, newDay, newNight, totalAmount });
	return { meterId, totalAmount };
}

async function createNewMeter(meterId, dayReading, nightReading) {
	const exists = await Meter.findOne({ meterId }).sort({ date: -1 });
	if (exists) return { error: "Лічильник з таким ID вже існує" };

	const tariff = await Tariff.findOne();
	if (!tariff) return { error: "Тарифів не знайдено" };

	const totalAmount = await calculateBill(0, 0, dayReading, nightReading, tariff);

	const newMeter = new Meter({
		meterId,
		previousDayReading: 0,
		previousNightReading: 0,
		currentDayReading: dayReading,
		currentNightReading: nightReading,
		totalAmount,
		date: new Date()
	});
	sendToQueue({ meterId, dayReading, nightReading, totalAmount });
	await newMeter.save();
	return { meterId, totalAmount 	};
}

const getAllMeters = () => Meter.find();

const getAllMeterIds = async () =>		(await Meter.find({}, "meterId")).map(m => m.meterId);

const getLatestReadings = async meterId => {
	const meter = await Meter.findOne({ meterId }).sort({ date: -1 });
	return meter
		? {
			meterId,
			currentDayReading: meter.currentDayReading,
			currentNightReading: meter.currentNightReading
		}
		: {
			meterId,
			currentDayReading: 0,
			currentNightReading: 0
		};
};

const getMeterHistory = meterId =>
  	Meter.find({ meterId }).sort({ date: -1 });

module.exports = {
	addMeterData,
	createNewMeter,
	getAllMeters,
	getAllMeterIds,
	getLatestReadings,
	getMeterHistory
};
