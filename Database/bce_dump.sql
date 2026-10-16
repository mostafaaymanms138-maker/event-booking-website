-- Bristol Community Events database schema and sample event data.
-- Includes example categories, venues and events; no user accounts.
CREATE DATABASE IF NOT EXISTS `bce`;
USE `bce`;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `booking_days` (
  `id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int DEFAULT NULL,
  `event_date` date NOT NULL,
  `day_price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `booking_id` (`booking_id`),
  CONSTRAINT `booking_days_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `bookings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `event_id` int DEFAULT NULL,
  `quantity` int DEFAULT '1',
  `is_student` tinyint(1) DEFAULT '0',
  `advance_discount_pct` decimal(5,2) DEFAULT '0.00',
  `student_discount_pct` decimal(5,2) DEFAULT '10.00',
  `base_price` decimal(10,2) DEFAULT NULL,
  `total_price` decimal(10,2) DEFAULT NULL,
  `status` enum('confirmed','cancelled','pending') DEFAULT NULL,
  `booking_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `cancellation_charge` decimal(10,2) DEFAULT '0.00',
  `reference` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference` (`reference`),
  KEY `user_id` (`user_id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  `date` date NOT NULL,
  `time` time DEFAULT NULL,
  `venue_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `price` decimal(10,2) DEFAULT '0.00',
  `tickets_total` int NOT NULL,
  `tickets_remaining` int NOT NULL,
  `conditions` varchar(200) DEFAULT NULL,
  `last_booking_date` date DEFAULT NULL,
  `is_multiday` tinyint(1) DEFAULT '0',
  `days_count` int DEFAULT '1',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `venue_id` (`venue_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `events_ibfk_1` FOREIGN KEY (`venue_id`) REFERENCES `venues` (`id`),
  CONSTRAINT `events_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `payment_method` varchar(50) DEFAULT NULL,
  `status` enum('paid','refunded','pending') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `booking_id` (`booking_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_student` tinyint(1) DEFAULT '0',
  `is_admin` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `venues` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `address` varchar(200) DEFAULT NULL,
  `capacity` int NOT NULL,
  `suitable_for` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `waiting_list` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `event_id` int DEFAULT NULL,
  `joined_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `notified` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `waiting_list_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `waiting_list_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
INSERT INTO categories (id, name) VALUES
  (1, 'Music'),
  (2, 'Workshop'),
  (3, 'Community');

INSERT INTO venues (id, name, address, capacity, suitable_for) VALUES
  (1, 'Bristol Community Hall', 'Bristol', 150, 'Community events and performances'),
  (2, 'Harbourside Centre', 'Bristol', 100, 'Workshops and exhibitions');

INSERT INTO events (
  id, name, description, date, time, venue_id, category_id, price,
  tickets_total, tickets_remaining, conditions, last_booking_date,
  is_multiday, days_count, is_active
) VALUES
  (
    1, 'Bristol Community Music Night',
    'A local music event featuring Bristol performers.',
    DATE_ADD(CURDATE(), INTERVAL 45 DAY), '19:00:00', 1, 1, 12.00,
    150, 150, 'All ages welcome.',
    DATE_SUB(DATE_ADD(CURDATE(), INTERVAL 45 DAY), INTERVAL 1 DAY),
    0, 1, 1
  ),
  (
    2, 'Creative Skills Workshop',
    'A practical workshop for local residents.',
    DATE_ADD(CURDATE(), INTERVAL 30 DAY), '14:00:00', 2, 2, 8.00,
    100, 100, 'Advance booking recommended.',
    DATE_SUB(DATE_ADD(CURDATE(), INTERVAL 30 DAY), INTERVAL 1 DAY),
    0, 1, 1
  ),
  (
    3, 'Community Meet-up',
    'A free event for people in the local community.',
    DATE_ADD(CURDATE(), INTERVAL 20 DAY), '11:00:00', 1, 3, 0.00,
    80, 80, 'Free entry.',
    DATE_SUB(DATE_ADD(CURDATE(), INTERVAL 20 DAY), INTERVAL 1 DAY),
    0, 1, 1
  );

SET FOREIGN_KEY_CHECKS = 1;

