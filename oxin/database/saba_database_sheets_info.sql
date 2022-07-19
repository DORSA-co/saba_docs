-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: saba_database
-- ------------------------------------------------------
-- Server version	8.0.28

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
-- Table structure for table `sheets_info`
--

DROP TABLE IF EXISTS `sheets_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sheets_info` (
  `id` int NOT NULL,
  `sheet_id` varchar(45) NOT NULL,
  `heat_number` varchar(45) DEFAULT NULL,
  `ps_number` varchar(45) DEFAULT NULL,
  `pdl_number` float DEFAULT NULL,
  `lenght` float DEFAULT NULL,
  `width` float DEFAULT NULL,
  `thickness` float DEFAULT NULL,
  `user` varchar(45) DEFAULT NULL,
  `time` varchar(45) DEFAULT NULL,
  `date` varchar(45) DEFAULT NULL,
  `main_path` varchar(45) DEFAULT NULL,
  `nframe` int DEFAULT '0',
  `cameras` varchar(45) DEFAULT '0-12',
  `image_format` varchar(10) DEFAULT '.jpg',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sheets_info`
--

LOCK TABLES `sheets_info` WRITE;
/*!40000 ALTER TABLE `sheets_info` DISABLE KEYS */;
INSERT INTO `sheets_info` VALUES (0,'996','0','1111',2222,1000,480,NULL,'amir','12:15','1400/12/25','oxin_image_grabber',20,'0-12','.png'),(1,'997','0','1111',2222,1500,300,NULL,'milad','14:00','1400/12/25','oxin_image_grabber',25,'0-8','.png'),(2,'920','1','12',345,5000,120,NULL,NULL,NULL,'1400/12/25','oxin_image_grabber',20,'0-12','.png');
/*!40000 ALTER TABLE `sheets_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-06-29 11:51:41
