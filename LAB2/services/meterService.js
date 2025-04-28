const meters = require("../models/meterModel");
const tariffs = require("../models/tariffModel");

function getAllMeters() {
	
	if (meters.length > 0)
	  return meters;
	else 
	  return { error: "Немає даних лічильників" };
}

function calculateBill(previousDay, previousNight, currentDay, currentNight, tariffs) {
  const dayConsumption = currentDay - previousDay;
  const nightConsumption = currentNight - previousNight;

  const dayAmount = dayConsumption * tariffs.dayRate;
  const nightAmount = nightConsumption * tariffs.nightRate;

  return dayAmount + nightAmount;
}

function addNewMeter(meterId, dayReading, nightReading) {
	const newMeter = {
	  meterId,
	  previousDayReading: 0,
	  previousNightReading: 0,
	  currentDayReading: dayReading,
	  currentNightReading: nightReading,
	  tariffs,
	  date: new Date().toISOString(),
	  totalAmount: calculateBill(0, 0, dayReading, nightReading, tariffs)
	};
  
	meters.push(newMeter);
  
	return { meterId, totalAmount: newMeter.totalAmount };
  }
function updateMeterData(meterId, newDayReading, newNightReading) {
  const meter = meters.find(m => m.meterId === meterId);
  
  if (meter) {
    if (newDayReading < meter.currentDayReading) {
      newDayReading = meter.currentDayReading + tariffs.dayAdjustment;
    }
    if (newNightReading < meter.currentNightReading) {
      newNightReading = meter.currentNightReading + tariffs.nightAdjustment;
    }

    meter.previousDayReading = meter.currentDayReading;
    meter.previousNightReading = meter.currentNightReading;
    meter.currentDayReading = newDayReading;
    meter.currentNightReading = newNightReading;
    meter.totalAmount = calculateBill(
      meter.previousDayReading,
      meter.previousNightReading,
      meter.currentDayReading,
      meter.currentNightReading,
      tariffs
    );
    meter.date = new Date().toISOString();
	console.log("Updated meter:", meter);
    return { meterId, totalAmount: meter.totalAmount };
  } else {
    return { error: "Meter not found" };
  }
}


module.exports = {
  updateMeterData,
  addNewMeter
};
