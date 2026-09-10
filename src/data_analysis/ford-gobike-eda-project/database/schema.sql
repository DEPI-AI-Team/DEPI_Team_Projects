-- مسح الجداول القديمة لإعادة بنائها بالشروط والـ Indexes الجديدة
DROP TABLE IF EXISTS fact_trips CASCADE;
DROP TABLE IF EXISTS dim_time CASCADE;
DROP TABLE IF EXISTS dim_station CASCADE;
DROP TABLE IF EXISTS dim_user CASCADE;

-- 1. جدول المستخدمين (dim_user)
CREATE TABLE IF NOT EXISTS dim_user (
    user_id SERIAL PRIMARY KEY,
    birth_year INT,
    age INT CHECK (age > 0 AND age < 120),
    gender VARCHAR(20),
    user_type VARCHAR(50)
);

-- 2. جدول المحطات (dim_station)
CREATE TABLE IF NOT EXISTS dim_station (
    station_id INT PRIMARY KEY,
    station_name VARCHAR(255) NOT NULL,
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6)
);

-- 3. جدول الوقت (dim_time)
CREATE TABLE IF NOT EXISTS dim_time (
    time_id SERIAL PRIMARY KEY,
    date DATE,
    hour INT,
    day INT,
    day_of_week VARCHAR(20),
    month INT,
    year INT
);

-- 4. جدول الرحلات الرئيسي (fact_trips)
CREATE TABLE IF NOT EXISTS fact_trips (
    trip_id SERIAL PRIMARY KEY,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_sec INT NOT NULL CHECK (duration_sec > 0),
    bike_id INT,
    start_station_id INT NOT NULL REFERENCES dim_station(station_id),
    end_station_id   INT NOT NULL REFERENCES dim_station(station_id),
    user_id          INT NOT NULL REFERENCES dim_user(user_id),
    time_id          INT NOT NULL REFERENCES dim_time(time_id)
);

CREATE INDEX idx_fact_trips_start_station ON fact_trips(start_station_id);
CREATE INDEX idx_fact_trips_end_station ON fact_trips(end_station_id);
CREATE INDEX idx_fact_trips_user ON fact_trips(user_id);
CREATE INDEX idx_fact_trips_time ON fact_trips(time_id);