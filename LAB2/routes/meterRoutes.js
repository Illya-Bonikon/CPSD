const express = require("express");
const router = express.Router();
const {
	handleMeterData,
	handleNewMeter,
	getAllMeterIds,
	getMeterHistory,
	getLatestReadings
} = require("../controllers/meterController");

router
	.post("/add-data", handleMeterData)
	.post("/new", handleNewMeter)
	.get("/ids", getAllMeterIds)
	.get("/:meterId/history", getMeterHistory)
	.get("/:id/latest", getLatestReadings);

module.exports = router;
