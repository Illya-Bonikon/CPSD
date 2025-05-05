const Meter = require("../models/meterModel");
const Tariff = require("../models/tariffModel");
const mongoose = require("mongoose");

async function calculateBill(previousDay, previousNight, currentDay, currentNight, tariff) {
  const dayConsumption = currentDay - previousDay;
  const nightConsumption = currentNight - previousNight;
  
  const dayAmount = dayConsumption * tariff.dayRate;
  const nightAmount = nightConsumption * tariff.nightRate;

  return dayAmount + nightAmount;
}

async function updateMeterData(meterId, newDayReading, newNightReading) {
  const meter = await Meter.findOne({ meterId });
  const tariff = await Tariff.findOne(); 

  if (!meter) {
    return { error: "Лічильник не знайдено" };
  }

  if (newDayReading < meter.currentDayReading) {
    newDayReading = meter.currentDayReading + tariff.dayThreshold;
  }
  if (newNightReading < meter.currentNightReading) {
    newNightReading = meter.currentNightReading + tariff.nightThreshold;
  }

  meter.previousDayReading = meter.currentDayReading;
  meter.previousNightReading = meter.currentNightReading;
  meter.currentDayReading = newDayReading;
  meter.currentNightReading = newNightReading;
  meter.totalAmount = await calculateBill(
    meter.previousDayReading,
    meter.previousNightReading,
    meter.currentDayReading,
    meter.currentNightReading,
    tariff
  );
  meter.date = new Date();

  await meter.save();

  return { meterId: meter.meterId, totalAmount: meter.totalAmount };
}

async function addNewMeter(meterId, dayReading, nightReading) {
	console.log("Mongoose connected?", mongoose.connection.readyState);

	console.log("Adding new meter:", meterId, dayReading, nightReading);
	
  const existingMeter = await Meter.findOne({ meterId });
  if (existingMeter) {
	console.log("Meter already exists:", existingMeter);	
    return { error: "Лічильник з таким ID вже існує" };
  }

  const tariff = await Tariff.findOne();
  if (!tariff) {
    return { error: "Тарифів не знайдено" };
  }

  const newMeter = new Meter({
    meterId,
    previousDayReading: 0,
    previousNightReading: 0,
    currentDayReading: dayReading,
    currentNightReading: nightReading,
    totalAmount: await calculateBill(0, 0, dayReading, nightReading, tariff),
    date: new Date()
  });

  await newMeter.save();
  console.log("New meter added:", newMeter);
  return { meterId: newMeter.meterId, totalAmount: newMeter.totalAmount };
}

async function getAllMeters() {
  return await Meter.find();
}

async function getAllMeterIds() {
	const meters = await Meter.find({}, "meterId");
	return meters.map(m => m.meterId);
}

async function getMeterHistory(meterId) {
	return await Meter.find({ meterId }).sort({ date: -1 });
}

module.exports = {
  updateMeterData,
  addNewMeter,
  getAllMeters,
  getAllMeterIds,
  getMeterHistory
};
