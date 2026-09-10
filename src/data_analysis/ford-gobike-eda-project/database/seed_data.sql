-- 1. إضافة بيانات تجريبية للمستخدمين (dim_user)
INSERT INTO dim_user (birth_year, age, gender, user_type)
VALUES 
(1995, 29, 'Male', 'Subscriber'),
(1998, 26, 'Female', 'Customer'),
(1985, 39, 'Male', 'Subscriber'),
(2001, 23, 'Female', 'Customer'),
(1992, 32, 'Male', 'Subscriber');

-- 2. إضافة بيانات تجريبية للمحطات (dim_station)
INSERT INTO dim_station (station_id, station_name, latitude, longitude)
VALUES 
(58, 'Market St at 10th St', 37.776619, -122.417385),
(86, 'Market St at Dolores St', 37.769305, -122.426826),
(15, 'San Francisco Caltrain Station 2', 37.776598, -122.395282),
(21, 'Montgomery St BART Station', 37.789625, -122.400811),
(30, 'San Francisco Caltrain (Townsend St at 4th St)', 37.776598, -122.395282);

-- 3. إضافة بيانات متنوعة للوقت والتاريخ (dim_time)
INSERT INTO dim_time (date, hour, day, day_of_week, month, year)
VALUES 
('2019-02-28', 17, 28, 'Thursday', 2, 2019),
('2019-02-28', 18, 28, 'Thursday', 2, 2019),
('2019-02-27', 8,  27, 'Wednesday', 2, 2019),
('2019-02-27', 12, 27, 'Wednesday', 2, 2019),
('2019-02-26', 19, 26, 'Tuesday',   2, 2019),
('2019-02-25', 9,  25, 'Monday',    2, 2019);

-- 4. إضافة بيانات متنوعة للرحلات (fact_trips)
INSERT INTO fact_trips (start_time, end_time, duration_sec, bike_id, start_station_id, end_station_id, user_id, time_id)
VALUES 
('2019-02-28 17:32:10', '2019-02-28 18:01:47', 1777, 4135, 58, 86, 1, 1),
('2019-02-28 18:10:00', '2019-02-28 18:25:00', 900,  5210, 86, 15, 2, 2),
('2019-02-27 08:05:12', '2019-02-27 08:17:30', 738,  6122, 15, 21, 3, 3),
('2019-02-27 12:30:00', '2019-02-27 12:45:10', 910,  1432, 21, 30, 4, 4),
('2019-02-26 19:15:22', '2019-02-26 19:40:00', 1478, 3890, 30, 58, 5, 5),
('2019-02-25 09:00:00', '2019-02-25 09:12:00', 720,  2910, 58, 15, 1, 6);