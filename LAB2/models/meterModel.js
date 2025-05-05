const mongoose = require("mongoose");

const meterSchema = new mongoose.Schema({
  meterId: {
    type: String,
    required: true,
    unique: true,
	index: true,
  },
  previousDayReading: {
    type: Number,
    default: 0,
  },
  previousNightReading: {
    type: Number,
    default: 0,
  },
  currentDayReading: {
    type: Number,
    required: true,
  },
  currentNightReading: {
    type: Number,
    required: true,
  },
  totalAmount: {
    type: Number,
    default: 0,
  },
  date: {
    type: Date,
    default: Date.now,
  }
});

const Meter = mongoose.model("Meter", meterSchema);

module.exports = Meter;
