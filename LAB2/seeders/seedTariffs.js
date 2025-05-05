const mongoose = require("mongoose");
const Tariff = require("../models/tariffModel");

async function seedTariff() {
  try {
    // Перевірка, чи вже є тариф
    const existingTariff = await Tariff.countDocuments();
    if (existingTariff > 0) {
      console.log("Tariff already exists, skipping seed.");
      return; // Якщо тариф уже є, не додаємо новий
    }

    const tariff = {
      dayRate: 2.5,
      nightRate: 1.5,
      dayThreshold: 100,
      nightThreshold: 50,
    };

    await Tariff.create(tariff);
    console.log("Tariff seeded");
  } catch (error) {
    console.error("Error seeding tariff:", error);
  } finally {
    mongoose.connection.close();
  }
}

module.exports = { seedTariff };
