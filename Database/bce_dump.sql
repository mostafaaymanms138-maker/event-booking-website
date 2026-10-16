 -- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: bce
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `booking_days`
--

DROP TABLE IF EXISTS `booking_days`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking_days` (
  `id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int DEFAULT NULL,
  `event_date` date NOT NULL,
  `day_price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `booking_id` (`booking_id`),
  CONSTRAINT `booking_days_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking_days`
--

LOCK TABLES `booking_days` WRITE;
/*!40000 ALTER TABLE `booking_days` DISABLE KEYS */;
INSERT INTO `booking_days` VALUES (1,1,'2026-05-12',38.25),(2,2,'2026-05-22',12.75);
/*!40000 ALTER TABLE `booking_days` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
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
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (1,2,1,2,1,15.00,10.00,25.00,38.25,'confirmed','2026-04-20 22:52:40',0.00,'BCE-2026-00001'),(2,3,4,1,0,15.00,0.00,15.00,12.75,'confirmed','2026-04-20 22:52:40',0.00,'BCE-2026-00002'),(3,4,1,1,1,5.00,10.00,25.00,21.38,'cancelled','2026-04-21 00:37:07',21.38,'BCE-2026-14001'),(4,4,2,1,1,5.00,10.00,0.00,0.00,'cancelled','2026-04-21 02:16:22',0.00,'BCE-2026-13272'),(5,4,2,1,1,5.00,10.00,0.00,0.00,'cancelled','2026-04-21 02:22:38',0.00,'BCE-2026-31708'),(6,4,2,1,1,5.00,10.00,0.00,0.00,'cancelled','2026-04-21 03:54:52',0.00,'BCE-2026-34306'),(7,4,1,1,1,5.00,10.00,25.00,21.38,'confirmed','2026-04-21 04:22:22',0.00,'BCE-2026-59154'),(8,4,5,3,1,15.00,10.00,35.00,80.33,'cancelled','2026-04-21 08:49:33',32.13,'BCE-2026-99911'),(9,4,2,1,1,5.00,10.00,0.00,0.00,'cancelled','2026-04-22 21:33:51',0.00,'BCE-2026-16655'),(10,4,7,1,1,15.00,10.00,0.00,0.00,'cancelled','2026-04-22 21:40:08',0.00,'BCE-2026-50295'),(11,5,1,1,1,5.00,10.00,25.00,21.38,'confirmed','2026-04-22 22:58:13',0.00,'BCE-2026-91563'),(12,5,2,1,1,5.00,10.00,0.00,0.00,'confirmed','2026-04-22 22:58:42',0.00,'BCE-2026-96765'),(13,4,2,1,1,5.00,10.00,0.00,0.00,'confirmed','2026-04-23 00:16:13',0.00,'BCE-2026-31138'),(18,14,1,3,1,5.00,10.00,25.00,64.12,'cancelled','2026-04-23 12:38:18',64.12,'BCE-2026-74725'),(19,14,8,2,1,15.00,10.00,0.00,0.00,'cancelled','2026-04-23 12:38:41',0.00,'BCE-2026-37000'),(20,4,2,1,1,5.00,10.00,0.00,0.00,'cancelled','2026-04-23 13:45:01',0.00,'BCE-2026-88369'),(21,4,5,4,1,15.00,10.00,35.00,107.10,'confirmed','2026-04-23 13:45:29',0.00,'BCE-2026-80359');
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Music'),(2,'Sports'),(3,'Exhibition'),(4,'Workshop'),(5,'Theatre'),(6,'Religious');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,'Bristol Jazz Night','Bristol Jazz Night returns to The Bristol Hippodrome for an unforgettable evening of live jazz. Featuring a curated line-up of local Bristol talent alongside acclaimed international performers, this is one of the most anticipated events on the cultural calendar.\nThe evening will feature three sets spanning classic bebop, contemporary cool jazz and Brazilian-influenced rhythms. A licensed bar will be open throughout, and light refreshments will be available. Smart casual dress code is strictly enforced.','2026-05-12','19:00:00',3,1,25.00,120,58,'Smart casual dress required','2026-05-10',0,1,1,'2026-04-20 22:52:40'),(2,'Modern Art at Arnolfini','A curated showcase of contemporary works by emerging and established artists from across the South West. The exhibition explores themes of urban identity, memory and transformation through painting, sculpture and mixed media.\nArnolfini is Bristol\'s leading centre for contemporary arts, and this free exhibition is part of the venue\'s commitment to making art accessible to everyone. Admission is free but booking is required to manage capacity. Guided tours run at 11:00 and 14:30.','2026-05-15','10:00:00',2,3,0.00,100,15,'No conditions','2026-05-13',0,1,1,'2026-04-20 22:52:40'),(3,'Bristol City FC Match','Bristol City FC take on a top-of-the-table rival in this high-stakes Championship fixture at Ashton Gate Stadium. The atmosphere on match days is electric, making this one of the most sought-after sporting events in Bristol this season.\nThis event is fully booked. Join the waiting list to be notified if tickets become available due to cancellations. Food and drink vendors open from doors, with a family area in the South Stand.','2026-05-20','15:00:00',1,2,50.00,150,0,'No conditions','2026-05-18',0,1,1,'2026-04-20 22:52:40'),(4,'Creative Writing Course','A three-hour creative writing workshop led by a published Bristol author. This session is designed for beginners and those who want to rediscover their love of writing, covering short fiction, personal narrative and poetry.\nAll materials are provided — no prior writing experience needed. The group is kept small (up to 15 participants) to ensure personal feedback from the tutor. Tea and coffee provided throughout.','2026-05-22','14:00:00',8,4,15.00,50,30,'No conditions','2026-05-20',0,1,1,'2026-04-20 22:52:40'),(5,'Hamlet at Bristol Old Vic','Bristol Old Vic presents a bold new production of Shakespeare\'s Hamlet, directed by award-winning director James Corwin. This intimate staging reimagines the classic tragedy in a contemporary setting, exploring themes of grief, indecision and political corruption.\nRunning approximately two hours and 45 minutes with one interval. A pre-show talk by the director takes place at 18:45, free for all ticket holders. Licensed bar and restaurant open from 18:00.','2026-05-28','19:30:00',4,5,35.00,110,41,'Smart dress recommended','2026-05-26',0,1,1,'2026-04-20 22:52:40'),(6,'Bristol Balloon Fiesta','The Bristol Balloon Fiesta is one of Europe\'s largest hot air balloon events, attracting over 150 balloons from across the world. The multi-day outdoor festival features twice-daily mass balloon ascents, evening night glows, and a fairground.\nA daily ticket covers all ground-based activities and balloon viewing. Balloon rides can be purchased separately on the day, subject to weather conditions. Over 60 food and drink traders on site.','2026-06-01','10:00:00',1,3,10.00,150,120,'No conditions','2026-05-29',1,5,1,'2026-04-20 22:52:40'),(7,'Community Prayers Evening','An inclusive community prayers evening open to people of all faiths and backgrounds. The event brings together Bristol\'s diverse communities for a shared evening of reflection, prayer and fellowship, organised by the Bristol Interfaith Forum.\nThe evening includes prayers and readings from multiple faith traditions, a shared meal, and a guest speaker on community cohesion in Bristol. All are welcome. A children\'s programme is available in the side room throughout the evening.','2026-06-05','18:00:00',10,6,0.00,60,40,'Respectful attire required','2026-06-03',0,1,1,'2026-04-20 22:52:40'),(8,'Bristol Photography Show','The Bristol Photography Show returns to the Royal West of England Academy with over 200 photographs selected from a city-wide open submission. This year\'s theme is Bristol Transformed — capturing change, resilience and beauty across the city\'s neighbourhoods.\nThe show features work from amateur and professional photographers alike, and all exhibited prints are available for purchase to support the artists. Free printed guide included with entry.','2026-06-10','11:00:00',6,3,0.00,100,80,'No conditions','2026-06-08',0,1,1,'2026-04-20 22:52:40'),(9,'Intro to Web Design','A full-day introductory workshop covering the fundamentals of modern web design, delivered by UWE Bristol\'s Digital Media team. The session is aimed at complete beginners and covers HTML, CSS, layout principles and visual design basics using free, industry-standard tools.\nBy the end of the day, participants will have built and published a simple personal webpage. Laptops are provided but you are welcome to bring your own. Lunch and refreshments are included.','2026-06-14','10:00:00',9,4,20.00,50,25,'Bring your own laptop','2026-06-12',0,1,1,'2026-04-20 22:52:40');
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `payment_method` varchar(50) DEFAULT NULL,
  `status` enum('paid','refunded','pending') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `booking_id` (`booking_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,1,38.25,'2026-04-20 22:52:40','card','paid'),(2,2,12.75,'2026-04-20 22:52:40','card','paid');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_student` tinyint(1) DEFAULT '0',
  `is_admin` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Admin User','admin@bce.co.uk','scrypt:32768:8:1$azH6LSUzS47Ljqpb$f149d8d8f3fd9fe885e8b18589b4549e890d1280f9bfb7d02482c6016a7377aff5b5fba2415f72841d211c524ece28dc82a348fe16a1fba1e59872b7598446a4',0,1,'2026-04-20 22:52:40'),(2,'John','john@gmail.com','$2b$12$placeholder_hash_here',1,0,'2026-04-20 22:52:40'),(3,'Jane Smith','jane@example.com','$2b$12$placeholder_hash_here',0,0,'2026-04-20 22:52:40'),(4,'Mostafa Ayman','mostafaa1@gmail.com','scrypt:32768:8:1$ljmMBwBAOFimuLub$4b05c590082503bc2fab16a66eb6aefbd82d242aaad6e1e746b3d8faff052bd55493aac2a3c3ce2d2c2b39011166cb86ffe1dddc5451242cd5956385cf43776d',1,0,'2026-04-21 00:35:50'),(5,'harry','harry@gmail.com','scrypt:32768:8:1$YbKyAW5WGZwKbw0E$9b13805f9c0467abdac0b9cf582e6d8a62bebf994a1ab6fd284391714b0b84aff0c17806384397a421187c957d2f8cacfcb7696a9beb639ecac9290994b41c19',1,0,'2026-04-22 22:57:06'),(13,'harvey','harvey@gmail.com','scrypt:32768:8:1$ori2yUmfirfQA9J6$08dd81c385f09d53ea3a341a90cade4dbd44ba3354b3ac42c8f71591796ec8a10779dbf40d8e64e1f640d391b4db201d435f3645620d2913d22de3a3ad0e7681',1,0,'2026-04-23 12:35:03'),(14,'Lewis mostafa','lewis@gmail.com','scrypt:32768:8:1$SnWxgbgxKzojNqq2$583f3e5ab1a12b4b61149b8de210f8cdfc0b2b17f31116a37d03150ad7a91db658a26d57b37fc957279b5299525adfa0ebfe57cdfc7d74889aa9c6acbfa635c6',1,0,'2026-04-23 12:37:26');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venues`
--

DROP TABLE IF EXISTS `venues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venues` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `address` varchar(200) DEFAULT NULL,
  `capacity` int NOT NULL,
  `suitable_for` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venues`
--

LOCK TABLES `venues` WRITE;
/*!40000 ALTER TABLE `venues` DISABLE KEYS */;
INSERT INTO `venues` VALUES (1,'Ashton Gate Stadium','Ashton Road, Bristol',150,'Music, Sports, Exhibitions'),(2,'Arnolfini','16 Narrow Quay, Bristol',100,'Exhibitions, Workshops'),(3,'The Bristol Hippodrome','St Augustines Parade, Bristol',120,'Theatre, Music'),(4,'Bristol Old Vic','King Street, Bristol',110,'Theatre'),(5,'Bristol Central Library','College Green, Bristol',50,'Library Exhibitions'),(6,'Royal West of England Academy','Queens Road, Bristol',100,'Exhibitions'),(7,'Creative Space A','Bristol City Centre',30,'Workshops'),(8,'Creative Space B','Bristol City Centre',50,'Workshops, Courses'),(9,'UWE Exhibition Centre','Frenchay Campus, Bristol',300,'Weddings, Workshops, Conferences'),(10,'Community Centre A','Bristol',60,'Private Events, Religious Events'),(12,'Ashton gate','Bristol',150,'sports'),(13,'ashton gate','bristol road',130,'music');
/*!40000 ALTER TABLE `venues` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `waiting_list`
--

DROP TABLE IF EXISTS `waiting_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waiting_list` (
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `waiting_list`
--

LOCK TABLES `waiting_list` WRITE;
/*!40000 ALTER TABLE `waiting_list` DISABLE KEYS */;
INSERT INTO `waiting_list` VALUES (1,3,3,'2026-04-20 22:52:40',0),(2,2,3,'2026-04-20 22:52:40',0),(3,4,3,'2026-04-21 00:36:27',0),(4,5,3,'2026-04-23 01:45:48',0),(6,14,3,'2026-04-23 12:37:48',0);
/*!40000 ALTER TABLE `waiting_list` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-23 15:07:59
