	CREATE DATABASE IF NOT EXISTS weather_prediction;
	USE weather_prediction;


	CREATE TABLE IF NOT EXISTS temperature_data (
		id INT AUTO_INCREMENT PRIMARY KEY,
		timestamp DATETIME NOT NULL,
		temperature FLOAT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		INDEX idx_temperature_data_timestamp (timestamp)
	);

	CREATE TABLE IF NOT EXISTS predictions (
		id INT AUTO_INCREMENT PRIMARY KEY,
		date DATE NOT NULL,
		min_temperature FLOAT NOT NULL,
		max_temperature FLOAT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		INDEX idx_predictions_date (date)
	);

	CREATE TABLE IF NOT EXISTS models_metadata (
		id INT AUTO_INCREMENT PRIMARY KEY,
		model_type VARCHAR(50) NOT NULL,
		training_date DATE NOT NULL,
		metrics TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);