const express = require("express");
const router = express.Router();
const meterController = require("../controllers/meterController");

router.post("/update", meterController.handleMeterData);   
router.post("/new", meterController.handleNewMeter);       
router.get("/", meterController.getAllMeterData);  
router.get("/ids", meterController.getAllMeterIds);
router.get("/:meterId/history", meterController.getMeterHistory);

module.exports = router;
