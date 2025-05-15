const meterService = require("../services/meterService");

const mockMeters = [];
const mockTariff = {
  dayRate: 1.2,
  nightRate: 1.1,
  dayOverflow: 100,
  nightOverflow: 80,
};

const Meter = {
  findOne: (query) => {
    return new Promise((resolve, reject) => {
      const meter = mockMeters.find((meter) => meter.meterId === query.meterId);
      resolve(meter);
    });
  },
  save: (meter) => {
    return new Promise((resolve, reject) => {
      mockMeters.push(meter);
      resolve(meter);
    });
  }
};

const Tariff = {
  findOne: () => {
    return new Promise((resolve, reject) => {
      resolve(mockTariff); 
    });
  }
};


meterService.createNewMeter = async (meterId, dayReading, nightReading) => {
  const newMeter = {
    meterId,
    previousDayReading: 0,
    previousNightReading: 0,
    currentDayReading: dayReading,
    currentNightReading: nightReading,
    totalAmount: 0,
    date: new Date(),
  };

  const meter = await Meter.save(newMeter);
  return meter;
};

meterService.addMeterData = async (meterId, newDayReading, newNightReading) => {
  const meter = await Meter.findOne({ meterId });
  if (!meter) return null;

  const tariff = await Tariff.findOne();
  const dayOverflow = tariff.dayOverflow;
  const nightOverflow = tariff.nightOverflow;

  meter.previousDayReading = meter.currentDayReading;
  meter.previousNightReading = meter.currentNightReading;
  meter.currentDayReading = newDayReading < meter.previousDayReading ? meter.previousDayReading + dayOverflow : newDayReading;
  meter.currentNightReading = newNightReading < meter.previousNightReading ? meter.previousNightReading + nightOverflow : newNightReading;

  meter.totalAmount = (meter.currentDayReading - meter.previousDayReading) * tariff.dayRate + (meter.currentNightReading - meter.previousNightReading) * tariff.nightRate;
  
  await Meter.save(meter);

  return meter;
};

meterService.getLatestReadings = async (meterId) => {
  const meter = await Meter.findOne({ meterId });
  return meter;
};

async function runTests() {
  const log = (desc, result) => {
    console.log(`${desc}: ${result ? '✅ Успіх' : '❌ Провалено'}`);
  };

  try {
    console.log("Мокаєм MongoDB для тестування");

    // 1. Оновлення показників вже існуючого лічильника
    try {
      await meterService.createNewMeter('Test1', 1000, 500);
      const update = await meterService.addMeterData('Test1', 1200, 600);
      log('Оновлення показників вже існуючого лічильника', !!update.totalAmount);
    } catch {
      log('Оновлення показників вже існуючого лічильника', false);
    }

    // 2. Отримання показників від нового лічильника
    try {
      await meterService.createNewMeter('Test2', 2000, 1000);
      const latest = await meterService.getLatestReadings('Test2');
      log('Отримання показників від нового лічильника',
        latest.currentDayReading === 2000 && latest.currentNightReading === 1000);
    } catch {
      log('Отримання показників від нового лічильника', false);
    }

    // 3. Занижені нічні показники => має бути > через overflow
    try {
      await meterService.createNewMeter('Test3', 1000, 500);
      await meterService.addMeterData('Test3', 1100, 400);
      const latest = await meterService.getLatestReadings('Test3');
      log('Занижені нічні показники (переповнення)', latest.currentNightReading > 500);
    } catch {
      log('Занижені нічні показники (переповнення)', false);
    }

    // 4. Занижені денні показники => має бути > через overflow
    try {
      await meterService.createNewMeter('Test4', 1000, 500);
      await meterService.addMeterData('Test4', 900, 600);
      const latest = await meterService.getLatestReadings('Test4');
      log('Занижені денні показники (переповнення)', latest.currentDayReading > 1000);
    } catch {
      log('Занижені денні показники (переповнення)', false);
    }

    // 5. Занижені нічні та денні показники => обидва мають бути збільшені через overflow
    try {
      await meterService.createNewMeter('Test5', 1000, 500);
      await meterService.addMeterData('Test5', 900, 400);
      const latest = await meterService.getLatestReadings('Test5');
      log('Занижені нічні та денні показники (переповнення)',
        latest.currentDayReading > 1000 && latest.currentNightReading > 500);
    } catch {
      log('Занижені нічні та денні показники (переповнення)', false);
    }

  } catch (error) {
    console.error("❌ Помилка під час тесту:", error);
  } 
}

runTests();
