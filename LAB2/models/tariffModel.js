const mongoose = require("mongoose");

const tariffSchema = new mongoose.Schema({
	tariffName: { 
		type: String, 
		unique: true, 
		required: true,
		default: "Default Tariff"
	},
	dayRate: {
		type: Number,
		required: true,
	},
	nightRate: {
		type: Number,
		required: true,
	},
	dayOverflow: {
		type: Number,
		required: true,
		default: 100,
	},
	nightOverflow: {
		type: Number,
		required: true,
		default: 80,
	},
});

const Tariff = mongoose.model("Tariff", tariffSchema);

module.exports = Tariff;
