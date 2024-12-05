-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 05, 2024 at 12:27 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `investment_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `alternatives`
--

CREATE TABLE `alternatives` (
  `id` int(11) NOT NULL,
  `sector` varchar(255) NOT NULL,
  `c_to_c_growth` float NOT NULL,
  `q_to_q_growth` float NOT NULL,
  `y_on_y_growth` float NOT NULL,
  `unemployment` float NOT NULL,
  `inflation` float NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alternatives`
--

INSERT INTO `alternatives` (`id`, `sector`, `c_to_c_growth`, `q_to_q_growth`, `y_on_y_growth`, `unemployment`, `inflation`, `user_id`) VALUES
(371, 'Tanaman Perkebunan', 2.74, 2.12, 1.96, 6.11, 3.37, 0),
(372, 'Peternakan', 2.25, 2.83, 3.83, 1.79, 3.81, 0),
(373, 'Perikanan', 4.39, 2.62, 5.4, 6.39, 2.14, 0),
(374, 'Industri Makanan dan Minuman', 4.73, 1.83, 4.48, 5.14, 3.2, 0),
(375, 'Industri Kulit  Barang dari Kulit dan Alas Kaki', 1.41, 0.91, 0.3, 4.01, 2.61, 0),
(376, 'Industri Kayu  Barang dari Kayu dan Gabus dan Barang Anyaman dari Bambu Rotan dan Sejenisnya', 1.66, 1.46, 1.35, 5.85, 2.56, 0),
(377, 'Industri Kimia  Farmasi dan Obat Tradisional', 1.18, 0.24, 0.12, 4.78, 2.28, 0),
(378, 'Industri Barang Logam; Komputer Barang Elektronik Optik; dan Peralatan Listrik', 13.94, 4.89, 13.71, 4.78, 2.54, 0),
(379, 'Industri Mesin dan Perlengkapan', 0.48, 0.49, 0.04, 2.94, 2.68, 0),
(380, 'Industri Alat Angkutan', 11.5, 1.17, 7.87, 1.32, 2.86, 0),
(381, 'Ketenagalistrikan', 3.66, 2.94, 5.06, 2.94, 3.81, 0),
(382, 'Pengadaan Gas dan Produksi Es', 4.98, 0.55, 3.55, 4.48, 2.77, 0),
(383, 'Pengadaan Air Pengelolaan Sampah Limbah dan Daur Ulang', 5.14, 1.91, 4.9, 3.9, 3.09, 0),
(384, 'Konstruksi', 3.36, 2.54, 4.91, 3.7, 2.28, 0),
(385, 'Perdagangan Mobil Sepeda Motor dan Reparasinya', 5.8, 0.81, 4.58, 2.94, 2.28, 0),
(386, 'Perdagangan Besar dan Eceran Bukan Mobil dan Sepeda Motor', 4.79, 2.01, 4.92, 4.03, 2.11, 0),
(387, 'Angkutan Darat', 9.18, 3.86, 9.65, 3.7, 2.28, 0),
(388, 'Angkutan Laut', 17.37, 4.67, 15.68, 3.57, 3.09, 0),
(389, 'Angkutan Sungai Danau dan Penyeberangan', 20.75, 4.49, 15.09, 4.22, 2.97, 0),
(390, 'Pergudangan dan Jasa Penunjang Angkutan; Pos dan Kurir', 20.26, 5.61, 18.19, 3.91, 2.32, 0),
(391, 'Penyediaan Akomodasi dan Makan Minum', 10.61, 3.56, 10.06, 4.46, 2.61, 0),
(392, 'Penyediaan Akomodasi', 13.69, 4.88, 13.12, 4.68, 3.04, 0),
(393, 'Penyediaan Makan Minum', 9.9, 3.25, 9.34, 3.05, 2.81, 0),
(394, 'Informasi dan Komunikasi', 7.55, 2.84, 7.6, 4.01, 2.32, 0),
(395, 'Perdagangan Anak', 1100, 4, 5, 7, 9, 0),
(396, 'Perdagangan Anaka', 1100, 4, 5, 7, 9, 0),
(397, 'Perdagangan Anaka', 1100, 4, 5, 7, 9, 0),
(398, 'Tanaman Perkebunan', 2.74, 2.12, 1.96, 6.11, 3.37, 0),
(399, 'Peternakan', 2.25, 2.83, 3.83, 1.79, 3.81, 0),
(400, 'Perikanan', 4.39, 2.62, 5.4, 6.39, 2.14, 0),
(401, 'Industri Makanan dan Minuman', 4.73, 1.83, 4.48, 5.14, 3.2, 0),
(402, 'Industri Kulit  Barang dari Kulit dan Alas Kaki', 1.41, 0.91, 0.3, 4.01, 2.61, 0),
(403, 'Industri Kayu  Barang dari Kayu dan Gabus dan Barang Anyaman dari Bambu Rotan dan Sejenisnya', 1.66, 1.46, 1.35, 5.85, 2.56, 0),
(404, 'Industri Kimia  Farmasi dan Obat Tradisional', 1.18, 0.24, 0.12, 4.78, 2.28, 0),
(405, 'Industri Barang Logam; Komputer Barang Elektronik Optik; dan Peralatan Listrik', 13.94, 4.89, 13.71, 4.78, 2.54, 0),
(406, 'Industri Mesin dan Perlengkapan', 0.48, 0.49, 0.04, 2.94, 2.68, 0),
(407, 'Industri Alat Angkutan', 11.5, 1.17, 7.87, 1.32, 2.86, 0),
(408, 'Ketenagalistrikan', 3.66, 2.94, 5.06, 2.94, 3.81, 0),
(409, 'Pengadaan Gas dan Produksi Es', 4.98, 0.55, 3.55, 4.48, 2.77, 0),
(410, 'Pengadaan Air Pengelolaan Sampah Limbah dan Daur Ulang', 5.14, 1.91, 4.9, 3.9, 3.09, 0),
(411, 'Konstruksi', 3.36, 2.54, 4.91, 3.7, 2.28, 0),
(412, 'Perdagangan Mobil Sepeda Motor dan Reparasinya', 5.8, 0.81, 4.58, 2.94, 2.28, 0),
(413, 'Perdagangan Besar dan Eceran Bukan Mobil dan Sepeda Motor', 4.79, 2.01, 4.92, 4.03, 2.11, 0),
(414, 'Angkutan Darat', 9.18, 3.86, 9.65, 3.7, 2.28, 0),
(415, 'Angkutan Laut', 17.37, 4.67, 15.68, 3.57, 3.09, 0),
(416, 'Angkutan Sungai Danau dan Penyeberangan', 20.75, 4.49, 15.09, 4.22, 2.97, 0),
(417, 'Pergudangan dan Jasa Penunjang Angkutan; Pos dan Kurir', 20.26, 5.61, 18.19, 3.91, 2.32, 0),
(418, 'Penyediaan Akomodasi dan Makan Minum', 10.61, 3.56, 10.06, 4.46, 2.61, 0),
(419, 'Penyediaan Akomodasi', 13.69, 4.88, 13.12, 4.68, 3.04, 0),
(420, 'Penyediaan Makan Minum', 9.9, 3.25, 9.34, 3.05, 2.81, 0),
(421, 'Informasi dan Komunikasi', 7.55, 2.84, 7.6, 4.01, 2.32, 0),
(472, 'Tanaman Perkebunan', 2.74, 2.12, 1.96, 6.11, 3.37, 1),
(473, 'Peternakan', 2.25, 2.83, 3.83, 1.79, 3.81, 1),
(474, 'Perikanan', 4.39, 2.62, 5.4, 6.39, 2.14, 1),
(475, 'Industri Makanan dan Minuman', 4.73, 1.83, 4.48, 5.14, 3.2, 1),
(476, 'Industri Kulit  Barang dari Kulit dan Alas Kaki', 1.41, 0.91, 0.3, 4.01, 2.61, 1),
(477, 'Industri Kayu  Barang dari Kayu dan Gabus dan Barang Anyaman dari Bambu Rotan dan Sejenisnya', 1.66, 1.46, 1.35, 5.85, 2.56, 1),
(478, 'Industri Kimia  Farmasi dan Obat Tradisional', 1.18, 0.24, 0.12, 4.78, 2.28, 1),
(479, 'Industri Barang Logam; Komputer Barang Elektronik Optik; dan Peralatan Listrik', 13.94, 4.89, 13.71, 4.78, 2.54, 1),
(480, 'Industri Mesin dan Perlengkapan', 0.48, 0.49, 0.04, 2.94, 2.68, 1),
(481, 'Industri Alat Angkutan', 11.5, 1.17, 7.87, 1.32, 2.86, 1),
(482, 'Ketenagalistrikan', 3.66, 2.94, 5.06, 2.94, 3.81, 1),
(483, 'Pengadaan Gas dan Produksi Es', 4.98, 0.55, 3.55, 4.48, 2.77, 1),
(484, 'Pengadaan Air Pengelolaan Sampah Limbah dan Daur Ulang', 5.14, 1.91, 4.9, 3.9, 3.09, 1),
(485, 'Konstruksi', 3.36, 2.54, 4.91, 3.7, 2.28, 1),
(486, 'Perdagangan Mobil Sepeda Motor dan Reparasinya', 5.8, 0.81, 4.58, 2.94, 2.28, 1),
(487, 'Perdagangan Besar dan Eceran Bukan Mobil dan Sepeda Motor', 4.79, 2.01, 4.92, 4.03, 2.11, 1),
(488, 'Angkutan Darat', 9.18, 3.86, 9.65, 3.7, 2.28, 1),
(489, 'Angkutan Laut', 17.37, 4.67, 15.68, 3.57, 3.09, 1),
(490, 'Angkutan Sungai Danau dan Penyeberangan', 20.75, 4.49, 15.09, 4.22, 2.97, 1),
(491, 'Pergudangan dan Jasa Penunjang Angkutan; Pos dan Kurir', 20.26, 5.61, 18.19, 3.91, 2.32, 1),
(492, 'Penyediaan Akomodasi dan Makan Minum', 10.61, 3.56, 10.06, 4.46, 2.61, 1),
(493, 'Penyediaan Akomodasi', 13.69, 4.88, 13.12, 4.68, 3.04, 1),
(494, 'Penyediaan Makan Minum', 9.9, 3.25, 9.34, 3.05, 2.81, 1),
(495, 'Informasi dan Komunikasi', 7.55, 2.84, 7.6, 4.01, 2.32, 1);

-- --------------------------------------------------------

--
-- Table structure for table `results`
--

CREATE TABLE `results` (
  `id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `sector` varchar(255) NOT NULL,
  `score` float NOT NULL,
  `rank` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `results`
--

INSERT INTO `results` (`id`, `filename`, `sector`, `score`, `rank`, `user_id`, `created_at`) VALUES
(289, 'alternatives_master.csv.csv', 'Pergudangan dan Jasa Penunjang Angkutan; Pos dan Kurir', 0.0952225, 1, 0, '2024-12-05 10:46:17'),
(290, 'alternatives_master.csv.csv', 'Angkutan Sungai Danau dan Penyeberangan', 0.088593, 2, 0, '2024-12-05 10:46:17'),
(291, 'alternatives_master.csv.csv', 'Angkutan Laut', 0.0852178, 3, 0, '2024-12-05 10:46:17'),
(292, 'alternatives_master.csv.csv', 'Industri Barang Logam; Komputer Barang Elektronik Optik; dan Peralatan Listrik', 0.073822, 4, 0, '2024-12-05 10:46:17'),
(293, 'alternatives_master.csv.csv', 'Penyediaan Akomodasi', 0.0735653, 5, 0, '2024-12-05 10:46:17'),
(294, 'alternatives_master.csv.csv', 'Penyediaan Akomodasi dan Makan Minum', 0.0579833, 6, 0, '2024-12-05 10:46:17'),
(295, 'alternatives_master.csv.csv', 'Penyediaan Makan Minum', 0.0564884, 7, 0, '2024-12-05 10:46:17'),
(296, 'alternatives_master.csv.csv', 'Angkutan Darat', 0.0557541, 8, 0, '2024-12-05 10:46:17'),
(297, 'alternatives_master.csv.csv', 'Industri Alat Angkutan', 0.0489138, 9, 0, '2024-12-05 10:46:17'),
(298, 'alternatives_master.csv.csv', 'Informasi dan Komunikasi', 0.0453021, 10, 0, '2024-12-05 10:46:17'),
(299, 'alternatives_master.csv.csv', 'Ketenagalistrikan', 0.0332408, 11, 0, '2024-12-05 10:46:17'),
(300, 'alternatives_master.csv.csv', 'Pengadaan Air Pengelolaan Sampah Limbah dan Daur Ulang', 0.032911, 12, 0, '2024-12-05 10:46:17'),
(301, 'alternatives_master.csv.csv', 'Perikanan', 0.0317368, 13, 0, '2024-12-05 10:46:17'),
(302, 'alternatives_master.csv.csv', 'Perdagangan Besar dan Eceran Bukan Mobil dan Sepeda Motor', 0.0315545, 14, 0, '2024-12-05 10:46:17'),
(303, 'alternatives_master.csv.csv', 'Industri Makanan dan Minuman', 0.0302363, 15, 0, '2024-12-05 10:46:17'),
(304, 'alternatives_master.csv.csv', 'Konstruksi', 0.0292176, 16, 0, '2024-12-05 10:46:17'),
(305, 'alternatives_master.csv.csv', 'Perdagangan Mobil Sepeda Motor dan Reparasinya', 0.0278783, 17, 0, '2024-12-05 10:46:17'),
(306, 'alternatives_master.csv.csv', 'Peternakan', 0.0267215, 18, 0, '2024-12-05 10:46:17'),
(307, 'alternatives_master.csv.csv', 'Pengadaan Gas dan Produksi Es', 0.0220933, 19, 0, '2024-12-05 10:46:17'),
(308, 'alternatives_master.csv.csv', 'Tanaman Perkebunan', 0.0211024, 20, 0, '2024-12-05 10:46:17'),
(309, 'alternatives_master.csv.csv', 'Industri Kayu  Barang dari Kayu dan Gabus dan Barang Anyaman dari Bambu Rotan dan Sejenisnya', 0.0144007, 21, 0, '2024-12-05 10:46:17'),
(310, 'alternatives_master.csv.csv', 'Industri Kulit  Barang dari Kulit dan Alas Kaki', 0.00932182, 22, 0, '2024-12-05 10:46:17'),
(311, 'alternatives_master.csv.csv', 'Industri Kimia  Farmasi dan Obat Tradisional', 0.00512184, 23, 0, '2024-12-05 10:46:17'),
(312, 'alternatives_master.csv.csv', 'Industri Mesin dan Perlengkapan', 0.0036008, 24, 0, '2024-12-05 10:46:17'),
(2534, 'data.csv', 'Pergudangan dan Jasa Penunjang Angkutan; Pos dan Kurir', 0.0952225, 1, 0, '2024-12-05 10:46:17'),
(2535, 'data.csv', 'Angkutan Sungai Danau dan Penyeberangan', 0.088593, 2, 0, '2024-12-05 10:46:17'),
(2536, 'data.csv', 'Angkutan Laut', 0.0852178, 3, 0, '2024-12-05 10:46:17'),
(2537, 'data.csv', 'Industri Barang Logam; Komputer Barang Elektronik Optik; dan Peralatan Listrik', 0.073822, 4, 0, '2024-12-05 10:46:17'),
(2538, 'data.csv', 'Penyediaan Akomodasi', 0.0735653, 5, 0, '2024-12-05 10:46:17'),
(2539, 'data.csv', 'Penyediaan Akomodasi dan Makan Minum', 0.0579833, 6, 0, '2024-12-05 10:46:17'),
(2540, 'data.csv', 'Penyediaan Makan Minum', 0.0564884, 7, 0, '2024-12-05 10:46:17'),
(2541, 'data.csv', 'Angkutan Darat', 0.0557541, 8, 0, '2024-12-05 10:46:17'),
(2542, 'data.csv', 'Industri Alat Angkutan', 0.0489138, 9, 0, '2024-12-05 10:46:17'),
(2543, 'data.csv', 'Informasi dan Komunikasi', 0.0453021, 10, 0, '2024-12-05 10:46:17'),
(2544, 'data.csv', 'Ketenagalistrikan', 0.0332408, 11, 0, '2024-12-05 10:46:17'),
(2545, 'data.csv', 'Pengadaan Air Pengelolaan Sampah Limbah dan Daur Ulang', 0.032911, 12, 0, '2024-12-05 10:46:17'),
(2546, 'data.csv', 'Perikanan', 0.0317368, 13, 0, '2024-12-05 10:46:17'),
(2547, 'data.csv', 'Perdagangan Besar dan Eceran Bukan Mobil dan Sepeda Motor', 0.0315545, 14, 0, '2024-12-05 10:46:17'),
(2548, 'data.csv', 'Industri Makanan dan Minuman', 0.0302363, 15, 0, '2024-12-05 10:46:17'),
(2549, 'data.csv', 'Konstruksi', 0.0292176, 16, 0, '2024-12-05 10:46:17'),
(2550, 'data.csv', 'Perdagangan Mobil Sepeda Motor dan Reparasinya', 0.0278783, 17, 0, '2024-12-05 10:46:17'),
(2551, 'data.csv', 'Peternakan', 0.0267215, 18, 0, '2024-12-05 10:46:17'),
(2552, 'data.csv', 'Pengadaan Gas dan Produksi Es', 0.0220933, 19, 0, '2024-12-05 10:46:17'),
(2553, 'data.csv', 'Tanaman Perkebunan', 0.0211024, 20, 0, '2024-12-05 10:46:17'),
(2554, 'data.csv', 'Industri Kayu  Barang dari Kayu dan Gabus dan Barang Anyaman dari Bambu Rotan dan Sejenisnya', 0.0144007, 21, 0, '2024-12-05 10:46:17'),
(2555, 'data.csv', 'Industri Kulit  Barang dari Kulit dan Alas Kaki', 0.00932182, 22, 0, '2024-12-05 10:46:17'),
(2556, 'data.csv', 'Industri Kimia  Farmasi dan Obat Tradisional', 0.00512184, 23, 0, '2024-12-05 10:46:17'),
(2557, 'data.csv', 'Industri Mesin dan Perlengkapan', 0.0036008, 24, 0, '2024-12-05 10:46:17'),
(2996, 'data.csv', 'Pergudangan dan Jasa Penunjang Angkutan; Pos dan Kurir', 0.0952225, 1, 1, '2024-12-05 11:24:41'),
(2997, 'data.csv', 'Angkutan Sungai Danau dan Penyeberangan', 0.088593, 2, 1, '2024-12-05 11:24:41'),
(2998, 'data.csv', 'Angkutan Laut', 0.0852178, 3, 1, '2024-12-05 11:24:41'),
(2999, 'data.csv', 'Industri Barang Logam; Komputer Barang Elektronik Optik; dan Peralatan Listrik', 0.073822, 4, 1, '2024-12-05 11:24:41'),
(3000, 'data.csv', 'Penyediaan Akomodasi', 0.0735653, 5, 1, '2024-12-05 11:24:41'),
(3001, 'data.csv', 'Penyediaan Akomodasi dan Makan Minum', 0.0579833, 6, 1, '2024-12-05 11:24:41'),
(3002, 'data.csv', 'Penyediaan Makan Minum', 0.0564884, 7, 1, '2024-12-05 11:24:41'),
(3003, 'data.csv', 'Angkutan Darat', 0.0557541, 8, 1, '2024-12-05 11:24:41'),
(3004, 'data.csv', 'Industri Alat Angkutan', 0.0489138, 9, 1, '2024-12-05 11:24:41'),
(3005, 'data.csv', 'Informasi dan Komunikasi', 0.0453021, 10, 1, '2024-12-05 11:24:41'),
(3006, 'data.csv', 'Ketenagalistrikan', 0.0332408, 11, 1, '2024-12-05 11:24:41'),
(3007, 'data.csv', 'Pengadaan Air Pengelolaan Sampah Limbah dan Daur Ulang', 0.032911, 12, 1, '2024-12-05 11:24:41'),
(3008, 'data.csv', 'Perikanan', 0.0317368, 13, 1, '2024-12-05 11:24:41'),
(3009, 'data.csv', 'Perdagangan Besar dan Eceran Bukan Mobil dan Sepeda Motor', 0.0315545, 14, 1, '2024-12-05 11:24:41'),
(3010, 'data.csv', 'Industri Makanan dan Minuman', 0.0302363, 15, 1, '2024-12-05 11:24:41'),
(3011, 'data.csv', 'Konstruksi', 0.0292176, 16, 1, '2024-12-05 11:24:41'),
(3012, 'data.csv', 'Perdagangan Mobil Sepeda Motor dan Reparasinya', 0.0278783, 17, 1, '2024-12-05 11:24:41'),
(3013, 'data.csv', 'Peternakan', 0.0267215, 18, 1, '2024-12-05 11:24:41'),
(3014, 'data.csv', 'Pengadaan Gas dan Produksi Es', 0.0220933, 19, 1, '2024-12-05 11:24:41'),
(3015, 'data.csv', 'Tanaman Perkebunan', 0.0211024, 20, 1, '2024-12-05 11:24:41'),
(3016, 'data.csv', 'Industri Kayu  Barang dari Kayu dan Gabus dan Barang Anyaman dari Bambu Rotan dan Sejenisnya', 0.0144007, 21, 1, '2024-12-05 11:24:41'),
(3017, 'data.csv', 'Industri Kulit  Barang dari Kulit dan Alas Kaki', 0.00932182, 22, 1, '2024-12-05 11:24:41'),
(3018, 'data.csv', 'Industri Kimia  Farmasi dan Obat Tradisional', 0.00512184, 23, 1, '2024-12-05 11:24:41'),
(3019, 'data.csv', 'Industri Mesin dan Perlengkapan', 0.0036008, 24, 1, '2024-12-05 11:24:41');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `created_at`) VALUES
(1, 'firji', 'ijhonkjr07@gmail.com', '$2b$12$4od7cg1UPKGKGOY3wCbNhetc370M5zD7f5FxKEW3D4OQMBveCoFI.', '2024-12-05 10:41:31');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alternatives`
--
ALTER TABLE `alternatives`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `results`
--
ALTER TABLE `results`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `alternatives`
--
ALTER TABLE `alternatives`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=496;

--
-- AUTO_INCREMENT for table `results`
--
ALTER TABLE `results`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3020;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
