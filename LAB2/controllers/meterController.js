const meterService = require("../services/meterService");

async function handleMeterData(req, res) {
  try {
    const { meterId, newDayReading, newNightReading } = req.body;
    const result = await meterService.updateMeterData(meterId, newDayReading, newNightReading);
    res.json(result);
  } catch (error) {
    console.error("Помилка обробки даних лічильника:", error);
    res.status(500).json({ error: "Помилка сервера" });
  }
}

async function handleNewMeter(req, res) {
  try {
    const { meterId, dayReading, nightReading } = req.body;
    const result = await meterService.addNewMeter(meterId, dayReading, nightReading);
    res.json(result);
  } catch (error) {
    console.error("Помилка додавання нового лічильника:", error);
    res.status(500).json({ error: "Помилка сервера" });
  }
}

async function getAllMeterData(req, res) {
  try {
    const meters = await meterService.getAllMeters();
    res.json(meters);
  } catch (error) {
    console.error("Помилка отримання лічильників:", error);
    res.status(500).json({ error: "Помилка сервера" });
  }
}
async function getAllMeterIds(req, res) {
	try {
	  const ids = await meterService.getAllMeterIds();
	  res.json(ids);
	} catch (error) {
	  console.error("Помилка отримання ID:", error);
	  res.status(500).json({ error: "Помилка сервера" });
	}
  }
  
async function getMeterHistory(req, res) {
	try {
		const meterId = req.params.meterId;
		const history = await meterService.getMeterHistory(meterId);
		if (!history.length) {
		return res.status(404).json({ error: "Дані не знайдено" });
		}
		res.json(history);
	} catch (error) {
		console.error("Помилка історії:", error);
		res.status(500).json({ error: "Помилка сервера" });
	}
}


module.exports = {
  handleMeterData,
  handleNewMeter,
  getAllMeterData,
  getAllMeterIds,
  getMeterHistory
};
