-- phpMyAdmin SQL Dump
-- version 5.2.2deb1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 04, 2025 at 01:39 AM
-- Server version: 8.4.6-0ubuntu0.25.04.3
-- PHP Version: 8.4.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `oil_wells_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `stimulation_data`
--

CREATE TABLE `stimulation_data` (
  `id` int NOT NULL,
  `api_number` varchar(20) DEFAULT NULL,
  `date_stimulated` date DEFAULT NULL,
  `stimulated_formation` varchar(100) DEFAULT NULL,
  `top_ft` int DEFAULT NULL,
  `bottom_ft` int DEFAULT NULL,
  `stimulation_stages` int DEFAULT NULL,
  `volume` float DEFAULT NULL,
  `volume_units` varchar(50) DEFAULT NULL,
  `treatment_type` varchar(100) DEFAULT NULL,
  `acid_percent` float DEFAULT NULL,
  `lbs_proppant` bigint DEFAULT NULL,
  `max_pressure_psi` int DEFAULT NULL,
  `max_rate_bbls_min` float DEFAULT NULL,
  `details` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Table structure for table `well_information`
--

CREATE TABLE `well_information` (
  `api_number` varchar(20) NOT NULL,
  `well_name` varchar(255) DEFAULT NULL,
  `operator_name` varchar(255) DEFAULT NULL,
  `latitude` varchar(50) DEFAULT NULL,
  `longitude` varchar(50) DEFAULT NULL,
  `datum` varchar(50) DEFAULT NULL,
  `surface_hole_location` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

--
-- Dumping data for table `well_information`
--

INSERT INTO `well_information` (`api_number`, `well_name`, `operator_name`, `latitude`, `longitude`, `datum`, `surface_hole_location`) VALUES
('33-053-00605', 'Kline Federal 5300 31-18 8B', 'Address', '48° 04\' 28.160 N', '103° 36\' 11.380 W', ')', 'Lot 3, Sec. 18, T153N, R100W (2523\' FSL & 238 FWL)'),
('33-053-02102', 'Basic Game & Fish 34-3', 'Telephone Number', NULL, '_', 'co', NULL),
('33-053-02148', '24-HOUR PRODUCTION RATE', 'Telephone Number', NULL, NULL, NULL, NULL),
('33-053-03846', 'Dahl Federal 2-15H', 'Representative', 'of Well Head', 'of Well Head', 'Used', NULL),
('33-053-03911', '24-HOUR PRODUCTION RA  TE', 'OASIS PETROLEUM NORTH AMERICA LLC Date/Time of Incident : 8/21/2014 12:00:00 AM NDIC File Number : 20864 Facility Number : Well or Facility Name : BRAY  5301 43-12H Type of Incident : Stuffing Box Leak Field Name : BAKER County : MCKENZIE Section : 12 Tow', 'of Well Head', '103° 36\' 43.250 W', 'Project', NULL),
('33-053-03943', '24-HOUR PRODUCTION RATE', '1 : 5', 'Origin:48° 44\' 0.000 N° Projection method is Lambe', 'Origin:0° 0\' 0.000 E°, Latitude Origin:48° 44\' 0.0', 'TVDs to System: North Reference: Unit System:', NULL),
('33-053-03944', '24-HOUR PRODUCTION RATE', 'Slawson Exploration Co., Inc.', '48\"03\'08.925\"', '103\"36\'23.042\"  West  (bottom  location)', 'Used', NULL),
('33-053-04069', '24-HOUR PRODUCTION RATE', 'SLAWSON EXPLORATION COMPANY, INC. Date/Time of Incident : 6/1/2013 12:00:00 AM NDIC File Number : 22731 Facility Number : Well or Facility Name : MAGNUM  3-36-25H Type of Incident : Treater Popoff Field Name : BAKER County : MCKENZIE Section : 36 Township', '48°01\'29.869\"', '103°36\'18.972\"', 'Used', NULL),
('33-053-04211', 'Ash Federal 5300 11-18T', 'OASIS PETROLEUM NORTH AMERICA LLC', '48°', '103°', NULL, NULL),
('33-053-04852', '24-HOUR PRODUCTION RATE', 'Continental Resources, Inc.', '48° 4\' 29.665 N', '103° 40\' 12.754 W', 'North American Datum 1983', NULL),
('33-053-04981', '24-HOUR PRODUCTION RATE', 'Oasis Petroleum North America', 'Longitude:', 'Position Uncertainty:', 'Project', NULL),
('33-053-05845', 'Qtr-Qtr', 'Oasis Petroleum North America', 'Longitude:', 'Datum:', 'Field:', 'GL Elevation:'),
('33-053-05849', 'LEWIS FEDERAL 5300 21-31 5B', 'Oasis Petroleum North America LLC', 'Longitude:', 'Datum:', ')', 'GL Elevation:'),
('33-053-05906', 'Wade Federal 5300 31-30 11T', 'Qtr-Qtr', '48° 02\' 38.97 N', '103° 36\' 09.79 W', 'Nad 83', 'Lot 3, Sec. 30, T153N, R100W (1,955\' FSL - 350\' FWL)'),
('33-053-05924', 'Chalmers 5301 44-24 2TR', 'Oasis Petroleum North America', 'of Well Head', 'of Well Head', 'Project', NULL),
('33-053-05943', '24-HOUR PRODUCTION RATE', 'Oasis Petroleum North America', '48° 02\' 32.13 N', '103° 36\' 11.41 W', 'Nad 83', 'Lot 4, Sec. 30, T153N, R100W (1,263\' FSL - 240\' FWL)'),
('33-053-05954', 'Wade Federal 5300 41-30 6B', 'Oasis', '(N/S ° \' \") Longitude (E/W ° \' \") Surface 0.00 0.0', '(E/W ° \' \") Surface 0.00 0.00 0.00 0.00 0.00 0.00 ', 'Vertical Section Azimuth: Vertical Section Origin:', NULL),
('33-053-05995', 'Wade Federal 5300 31-30 2B', 'Oasis Petroleum North America', '(N/S ° \' \") Longitude (E/W ° \' \") Surface 0.00 0.0', '(E/W ° \' \") Surface 0.00 0.00 0.00 0.00 0.00 0.00 ', 'Vertical Section Azimuth: Vertical Section Origin:', NULL),
('33-053-05998', 'Wade Federal 5300 41-30 7T', 'Oasis', '11423.00', '(E/W °  \' \") Surface 0.00 0.00 0.00 0.00 0.00 0.00', '& Coordinate System', NULL),
('33-053-06010', 'Chalmers 5301 44-24 3BR', 'OASIS PETROLEUM NORTH AMERICA LL', 'of Well Head', 'of Well Head', NULL, NULL),
('33-053-06011', '24-HOUR PRODUCTION RA  TE', 'OASIS PETROLEUM NORTH AMERICA LL', '48, 03\', 20.01\" N', 'of Well Head', NULL, NULL),
('33-053-06012', '24-HOUR PRODUCTION RATE', 'Telephone Number', 'of Well Head', 'of Well Head', NULL, NULL),
('33-053-06018', 'Chalmers 5300 21-19 5T', 'Oasis Petroleum North America', 'of Well Head', 'of Well Head', ')', NULL),
('33-053-06019', '24-HOUR PRODUCTION RATE', 'Oasis Petroleum North America', 'of Well Head', 'of Well Head', ')', NULL),
('33-053-06021', 'Chalmers 5300 21-19 8T', 'Oasis Petroleum North America', '48° 3\' 41 .300 N', '103° 36\' 10.110 W', ')', NULL),
('33-053-06022', '24-HOUR PRODUCTION RATE', 'Qtr-Qtr', '48° 03\' 40.65 N', '103° 36\' 10.11 W', ')', 'Lot 2 , Sec. 19, T1153N, R100W (2,292\' FNL & 326 FWL)'),
('33-053-06023', '24-HOUR PRODUCTION RATE', 'Oasis Petroleum North America LLC', '48° 03\' 40.97 N', '103° 36\' 10.11 W', ')', 'Lot 2 , Sec. 19, T1153N, R100W (2,259\' FNL & 326 FWL)'),
('33-053-06024', 'Chalmers 5300 21-19 11 B', 'Telephone Number', '48° 03\' 40.32 N', '103° 36\' 10.11 W', 'Nad 83', 'Lot 2 , Sec. 19, T1153N, R100W (2,325\' FNL & 326 FWL)'),
('33-053-06028', '24-HOUR PRODUCTION RATE', 'Oasis Petroleum North America', '48.068701 deg. N Longitude:', '405103.22', 'Thickness', NULL),
('33-053-06051', 'Wade Federla 5300 41-30 9B', 'Oasis', '(N/S ° \' \") Longitude (E/W ° \' \") Surface 0.00 0.0', '(E/W ° \' \") Surface 0.00 0.00 180.00 0.00 0.00 0.0', 'Vertical Section Azimuth: Vertical Section Origin:', NULL),
('33-053-06056', 'Kline Federal 5300 31-18 7T', 'Oasis Petroleum', '48° 04\' 27.840 N', '103° 36\' 11.380 W', ')', 'Lot 3, Sec. 18, T153N, R100W (2490\' FSL & 238 FWL)'),
('33-053-06057', 'Kline Federal 5300 31-18 6B', 'Oasis Petroleum North America', '48° 04\' 27.510 N', '103° 36\' 11.380 W', 'Nad 83', 'Lot 3, Sec. 18, T153N, R100W (2457\' FSL & 238 FWL)'),
('33-053-06129', 'Wade Federal 5300 21-30 12T', 'Telephone Number', 'of Well Head', '· 48° 2\' 55.140 N103° 36\' 10.970 W', 'Mean', NULL),
('33-053-06131', 'Wade Federal 5300 21-30 13B', 'Oasis Petroleum North America LLC', 'of Well Head', '103• 36\' 10.970 w', 'Project', NULL),
('33-053-06223', 'Kline Federal 5300 11-18 5B', 'Oasis Petroleum North America', 'Longitude:', '13.200 in', 'Map Zone:', NULL),
('33-053-06225', 'Kline Federal 5300 11-18 3T', 'Oasis Petroleum North America', '48° 04\' 45.090 N', '103° 36\' 10.590 W', 'Nad 83', 'Lot 1, Sec. 18, T153N, R100W (1020\' FNL & 290 FWL)'),
('33-053-06231', 'Gramma Federal 5300 41-3112B', 'Qtr-Qtr', '48° 01\' 34.22 N', '103° 36\' 10.35 W', 'Nad 83', 'Lot 4 , Sec. 31, T153N, R100W (647\' FSL & 320 FWL)'),
('33-053-06232', '24-HOUR PRODUCTION RATE', 'Oasis Petroleum North America LLC', '48° 01\' 34.88 N', '103° 36\' 10.35 W', 'Nad 83', 'Lot 4 , Sec. 31, T153N, R100W (713\' FSL & 320 FWL)'),
('33-053-06243', 'Kline Federal 5300 11-18 2B', 'Oasis', '48° 04\' 45.680 N', '103° 36\' 10.190 W', 'Nad 83', 'Lot 1, Sec. 18, T153N, R100W (960\' FNL & 318 FWL)'),
('33-053-06548', 'LEWIS FEDERAL 5300 11-31 3B', 'OASIS PETROLEUM NORTH AMERICA LLC.', 'Longitude:', '393129.76', 'North American Datum 1983', NULL),
('33-053-06549', 'Qtr-Qtr a', 'Telephone Number', 'Longitude:', '393162.02', 'North American Datum 1983', NULL),
('33-053-06755', '24-HOUR PRODUCTION RATE', 'Otr-Qtr', 'of Well Head', 'of Well Head', ')', NULL),
('33-053-08946', 'Qtr-Qtr', 'Telephone Number', 'Longitude:', '393064.15', 'North American Datum 1983', NULL),
('33-053-90244', '24-HOUR PRODUCTION RATE', 'foasis PETROLEUM NORTH AMERICA LLC', '48° 1\' 44.700 N Longitude:  103° 35\' 58.470 W', '103° 35\' 58.470 W', 'North American Datum 1983', NULL),
('33-105-02719', '• d Number', 'Continental Resources, Inc.', 'of Well Head', 'of Well Head', NULL, NULL),
('33-105-02720', 'Atlanta 13-6H', 'Co 1tinental Resources, Inc.', '48.109 deg', '-103.728 deg', 'is', NULL),
('33-105-02721', 'Spacing Unit Description', '!Telephone Number', '48.109 deg', 'Drill Depth Zero Vertical Datum to DDZ Vertical Se', 'to DDZ Vertical Section East Vertical Section Dept', NULL),
('33-105-02722', 'Section', 'Continental Resources', '48.11 deg', 'Drill Depth Zero Vertical Datum to DDZ Vertical Se', 'to DDZ Vertical Section East Vertical Section Dept', NULL),
('33-105-02723', 'Qtr-Qtr', 's shall not commence operations on a drill site until the 3rd business day following publication of the approved drilling permit on the NDIC - OGD Daily Activity Report.   If circumstances require operations to commence before the 3rd business  day  follo', 'of Well Head', 'of Well Head', NULL, NULL),
('33-105-02724', 'Atlanta Federal 9-6H', 's shall not commence operations on a drill site until the 3rd business day following publication of the approved drilling permit on the NDIC - OGD Daily Activity Report.   If circumstances require operations to commence before the 3rd business  day  follo', 'of Well Head', 'of Well Head', NULL, NULL),
('33-105-02725', 'Qtr-Qtr', 'Continental Resources, Inc.', 'of Well Head', 'of Well Head', NULL, NULL),
('33-105-02726', 'Section', 'Continental Resources, Inc.', 'of Well Head', 'of Well Head', NULL, NULL),
('33-105-02727', '24-HOUR PRODUCTION RATE', 'CONTINENTAL RESOURCES, INC. Date/Time of Incident : 2/6/2014 12:00:00 AM NDIC File Number : 23367 Facility Number : Well or Facility Name : ATLANTA FEDERAL  6-6H Type of Incident : Other Field Name : BAKER County : WILLIAMS Section : 6 Township : 153 Rang', 'of Well Head', 'of Well Head', NULL, NULL),
('33-105-02728', 'Atlanta Federal 5-6H', 's shall not commence operations on a drill site until the 3rd business day following publication of the approved drilling permit on the NDIC - OGD Daily Activity Report.   If circumstances require operations to commence before the 3rd business  day  follo', 'of Well Head', 'of Well Head', NULL, NULL),
('33-105-02729', 'Atlanta 4-6H', 'CONTINENTAL RESOURCES, INC. Date/Time of Incident : 11/1/2013 12:00:00 AM NDIC File Number : 23369 Facility Number : Well or Facility Name : ATLANTA  4-6H Type of Incident : Tank Overflow Field Name : BAKER County : WILLIAMS Section : 6 Township : 153 Ran', '48.1094 deg', '-103.7329 deg', 'is', NULL),
('33-105-02730', 'Atlanta 3-6H', 'Continental Resources, Inc.', '48.1094 deg', '-103.7312 deg', 'is', NULL),
('33-105-02731', 'Atlanta 2-6H', 'CONTINENTAL RESOURCES, INC. Date/Time of Incident : 10/27/2013 12:00:00 AM NDIC File Number : 23371 Facility Number : Well or Facility Name : ATLANTA  2-6H Type of Incident : Tank Overflow Field Name : BAKER County : WILLIAMS Section : 6 Township : 153 Ra', 'Longitude:', 'Position Uncertainty:', 'Project', NULL),
('33-105-02732', 'Atlanta 1-6H', 'Continental Resources, Inc.', '48.11 deg', '-103.73 deg', 'is', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `stimulation_data`
--
ALTER TABLE `stimulation_data`
  ADD PRIMARY KEY (`id`),
  ADD KEY `api_number` (`api_number`);

--
-- Indexes for table `well_information`
--
ALTER TABLE `well_information`
  ADD PRIMARY KEY (`api_number`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `stimulation_data`
--
ALTER TABLE `stimulation_data`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `stimulation_data`
--
ALTER TABLE `stimulation_data`
  ADD CONSTRAINT `stimulation_data_ibfk_1` FOREIGN KEY (`api_number`) REFERENCES `well_information` (`api_number`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
The most reliable field  I was able to extract is the api number and well name