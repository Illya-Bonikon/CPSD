const mongoose = require("mongoose");
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
    // Перевірка, чи вже є дані
    const existingMeters = await Meter.countDocuments();
    if (existingMeters > 0) {
      console.log("Meters already exist, skipping seed.");
      return; // Якщо є лічильники, не додаємо нові
    }

    await mongoose.connect("mongodb://localhost:27017/metersDB");
    await Meter.insertMany(meters);
    console.log("Meters seeded");
  } catch (error) {
    console.error("Error seeding meters:", error);
  } finally {
    mongoose.connection.close();
  }
}

module.exports = { seedMeters };
