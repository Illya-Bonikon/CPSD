const meterService = require("../services/meterService");

const handleNotFound = (res, message = "Дані не знайдено") => {
	return res.status(404).json({ error: message });
};

const meterController = {
	async handleMeterData(req, res) {
		const { meterId, newDayReading, newNightReading } = req.body;
		const result = await meterService.addMeterData(meterId, newDayReading, newNightReading);
		res.json(result);
	},

	async handleNewMeter(req, res) {
		const { meterId, dayReading, nightReading } = req.body;
		const result = await meterService.createNewMeter(meterId, dayReading, nightReading);
		res.json(result);
	},

	async getAllMeterData(req, res) {
		const meters = await meterService.getAllMeters();
		res.json(meters);
	},

	async getAllMeterIds(req, res) {
		const ids = await meterService.getAllMeterIds();
		res.json(ids);
	},

	async getLatestReadings(req, res) {
		const { id } = req.params;
		const result = await meterService.getLatestReadings(id);

		if (!result) return handleNotFound(res, "Лічильник або записи не знайдено");
		res.json(result);
		},

	async getMeterHistory(req, res) {
		const { meterId } = req.params;
		const history = await meterService.getMeterHistory(meterId);

		if (!history.length) return handleNotFound(res);
		res.json(history);
	}
};


const wrappedController = {};
Object.keys(meterController).forEach(key => {
	wrappedController[key] = errorHandler(meterController[key]);
});

module.exports = wrappedController;