const { updateMeterData, addNewMeter } = require("../services/meterService");
const meters = require("../models/meterModel");

function getAllMeterData(httpRequest, httpResponse) {
	const result = getAllMeters();
	if (result.error) {
	  httpResponse.status(404).json({ error: result.error });
	} else {
	  httpResponse.json(result);
	}
}

function handleMeterData(httpRequest, httpResponse) {
  const { meterId, newDayReading, newNightReading } = httpRequest.body;
  console.log("Received data for updating meter:", { meterId, newDayReading, newNightReading });

  const result = updateMeterData(meterId, newDayReading, newNightReading);
  console.log("Update result:", result);

  if (result.error) 
    httpResponse.status(404).json({ error: result.error });
  else 
    httpResponse.json(result);

}

function handleNewMeter(httpRequest, httpResponse) {
  const { meterId, dayReading, nightReading } = httpRequest.body;
  console.log("Received data for new meter:", { meterId, dayReading, nightReading });

  const result = addNewMeter(meterId, dayReading, nightReading);
  console.log("New meter result:", result);

  httpResponse.json(result);
}

module.exports = {
	getAllMeterData,
	handleMeterData,
	handleNewMeter
};
