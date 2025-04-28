// TODO: make mongoose model for meter
const meters = [
	{
	  meterId: 'MTR-001',
	  previousDayReading: 100,
	  previousNightReading: 80,
	  currentDayReading: 120,
	  currentNightReading: 100,
	  date: '2025-04-28T10:00:00',
	  totalAmount: 0
	},
	{
	  meterId: 'MTR-002',
	  previousDayReading: 150,
	  previousNightReading: 130,
	  currentDayReading: 180,
	  currentNightReading: 150,
	  date: '2025-04-28T10:30:00',
	  totalAmount: 0
	}
];

module.exports = meters;
  