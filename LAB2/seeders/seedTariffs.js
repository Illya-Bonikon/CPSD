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
      tariffName: "Default Tariff",
      dayRate: 2.5,
      nightRate: 1.5,
      dayOverflow: 100,
      nightOverflow: 80,
    };
    
    await Tariff.create(tariff);
    console.log("Tariff seeded successfully");
  } catch (error) {
    console.error("Error seeding tariff:", error);
  }
}

module.exports = { seedTariff };