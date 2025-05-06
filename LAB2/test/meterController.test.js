const meterService = require("../services/meterService");

async function runTests() {
  const log = (desc, result) => {
    console.log(`${desc}: ${result ? '✅ PASSED' : '❌ FAILED'}`);
  };

  // [1] Оновлення показників вже існуючого лічильника
  try {
    await meterService.createNewMeter('Test1', 1000, 500);
    const update = await meterService.addMeterData('Test1', 1200, 600);
    log('Оновлення показників вже існуючого лічильника', !!update.totalAmount);
  } catch {
    log('Оновлення показників вже існуючого лічильника', false);
  }

  // [2] Отримання показників від нового лічильника
  try {
    await meterService.createNewMeter('Test2', 2000, 1000);
    const latest = await meterService.getLatestReadings('Test2');
    log('Отримання показників від нового лічильника', 
      latest.currentDayReading === 2000 && latest.currentNightReading === 1000);
  } catch {
    log('Отримання показників від нового лічильника', false);
  }

  // [3] Занижені нічні показники => має бути > через overflow
  try {
    await meterService.createNewMeter('Test3', 1000, 500);
    await meterService.addMeterData('Test3', 1100, 400); 
    const latest = await meterService.getLatestReadings('Test3');
    log('Занижені нічні показники (переповнення)', latest.currentNightReading > 500);
  } catch {
    log('Занижені нічні показники (переповнення)', false);
  }

  // [4] Занижені денні показники => має бути > через overflow
  try {
    await meterService.createNewMeter('Test4', 1000, 500);
    await meterService.addMeterData('Test4', 900, 600); 
    const latest = await meterService.getLatestReadings('Test4');
    log('Занижені денні показники (переповнення)', latest.currentDayReading > 1000);
  } catch {
    log('Занижені денні показники (переповнення)', false);
  }

  // [5] Занижені нічні та денні показники => обидва мають бути збільшені через overflow
  try {
    await meterService.createNewMeter('Test5', 1000, 500);
    await meterService.addMeterData('Test5', 900, 400); // обидва зменшено
    const latest = await meterService.getLatestReadings('Test5');
    log('Занижені нічні та денні показники (переповнення)',
      latest.currentDayReading > 1000 && latest.currentNightReading > 500);
  } catch {
    log('Занижені нічні та денні показники (переповнення)', false);
  }
}

runTests();
