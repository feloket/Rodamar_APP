
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `logistica_buque`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logistica_buque` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_viaje` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_atraque` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `buque_viaje_unico` (`nombre`,`numero_viaje`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `logistica_camionciguena`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logistica_camionciguena` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `patente` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `empresa_transporte` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre_chofer` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rut_chofer` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `patente` (`patente`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `logistica_cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logistica_cliente` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_completo` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rut_o_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rut_o_id` (`rut_o_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `logistica_historialestado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logistica_historialestado` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `estado_anterior` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado_nuevo` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ubicacion_anterior` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ubicacion_nueva` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `usuario_texto` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nota` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `usuario_id` int DEFAULT NULL,
  `vehiculo_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `logistica_historialestado_usuario_id_f03ac9d8_fk_auth_user_id` (`usuario_id`),
  KEY `logistica_historiale_vehiculo_id_0cd651d8_fk_logistica` (`vehiculo_id`),
  KEY `logistica_historialestado_fecha_65d6845e` (`fecha`),
  CONSTRAINT `logistica_historiale_vehiculo_id_0cd651d8_fk_logistica` FOREIGN KEY (`vehiculo_id`) REFERENCES `logistica_vehiculo` (`id`),
  CONSTRAINT `logistica_historialestado_usuario_id_f03ac9d8_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `logistica_vehiculo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logistica_vehiculo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `chasis` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `marca` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `modelo` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ubicacion_patio` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_registro` datetime(6) NOT NULL,
  `buque_id` bigint NOT NULL,
  `camion_ciguena_id` bigint DEFAULT NULL,
  `cliente_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chasis` (`chasis`),
  KEY `logistica_vehiculo_buque_id_3f9b2541_fk_logistica_buque_id` (`buque_id`),
  KEY `logistica_vehiculo_camion_ciguena_id_16814904_fk_logistica` (`camion_ciguena_id`),
  KEY `logistica_vehiculo_cliente_id_63d575f8_fk_logistica_cliente_id` (`cliente_id`),
  CONSTRAINT `logistica_vehiculo_buque_id_3f9b2541_fk_logistica_buque_id` FOREIGN KEY (`buque_id`) REFERENCES `logistica_buque` (`id`),
  CONSTRAINT `logistica_vehiculo_camion_ciguena_id_16814904_fk_logistica` FOREIGN KEY (`camion_ciguena_id`) REFERENCES `logistica_camionciguena` (`id`),
  CONSTRAINT `logistica_vehiculo_cliente_id_63d575f8_fk_logistica_cliente_id` FOREIGN KEY (`cliente_id`) REFERENCES `logistica_cliente` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `usuarios_perfil`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_perfil` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `empresa_id` bigint DEFAULT NULL,
  `usuario_id` int NOT NULL,
  `email_confirmado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  KEY `usuarios_perfil_empresa_id_faa3c16a_fk_logistica_cliente_id` (`empresa_id`),
  CONSTRAINT `usuarios_perfil_empresa_id_faa3c16a_fk_logistica_cliente_id` FOREIGN KEY (`empresa_id`) REFERENCES `logistica_cliente` (`id`),
  CONSTRAINT `usuarios_perfil_usuario_id_ca6ea2f9_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `usuarios_registroauditoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_registroauditoria` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha` datetime(6) NOT NULL,
  `accion` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `usuario_afectado_texto` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `objeto` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `campo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `valor_anterior` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `valor_nuevo` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `detalle` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `actor_id` int DEFAULT NULL,
  `usuario_afectado_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuarios_registroauditoria_actor_id_d464b1e8_fk_auth_user_id` (`actor_id`),
  KEY `usuarios_registroaud_usuario_afectado_id_a7d9b3d4_fk_auth_user` (`usuario_afectado_id`),
  KEY `usuarios_registroauditoria_fecha_ddd8632d` (`fecha`),
  KEY `usuarios_registroauditoria_accion_b5ec3f7e` (`accion`),
  CONSTRAINT `usuarios_registroaud_usuario_afectado_id_a7d9b3d4_fk_auth_user` FOREIGN KEY (`usuario_afectado_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `usuarios_registroauditoria_actor_id_d464b1e8_fk_auth_user_id` FOREIGN KEY (`actor_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (2,'Clientes'),(1,'Empleados');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add buque',7,'add_buque'),(26,'Can change buque',7,'change_buque'),(27,'Can delete buque',7,'delete_buque'),(28,'Can view buque',7,'view_buque'),(29,'Can add camion ciguena',8,'add_camionciguena'),(30,'Can change camion ciguena',8,'change_camionciguena'),(31,'Can delete camion ciguena',8,'delete_camionciguena'),(32,'Can view camion ciguena',8,'view_camionciguena'),(33,'Can add cliente',9,'add_cliente'),(34,'Can change cliente',9,'change_cliente'),(35,'Can delete cliente',9,'delete_cliente'),(36,'Can view cliente',9,'view_cliente'),(37,'Can add vehiculo',10,'add_vehiculo'),(38,'Can change vehiculo',10,'change_vehiculo'),(39,'Can delete vehiculo',10,'delete_vehiculo'),(40,'Can view vehiculo',10,'view_vehiculo'),(41,'Can add Historial de estado',11,'add_historialestado'),(42,'Can change Historial de estado',11,'change_historialestado'),(43,'Can delete Historial de estado',11,'delete_historialestado'),(44,'Can view Historial de estado',11,'view_historialestado'),(45,'Can add Perfil',12,'add_perfil'),(46,'Can change Perfil',12,'change_perfil'),(47,'Can delete Perfil',12,'delete_perfil'),(48,'Can view Perfil',12,'view_perfil'),(49,'Can add Registro de auditoría',13,'add_registroauditoria'),(50,'Can change Registro de auditoría',13,'change_registroauditoria'),(51,'Can delete Registro de auditoría',13,'delete_registroauditoria'),(52,'Can view Registro de auditoría',13,'view_registroauditoria');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$VHWxUqFYogMRHVL6ShkFh8$2acIJTX0s1yHK6kjLDFca13wVhUVAsy1LeG2sjvWvGA=',NULL,1,'admin_demo','Alicia','Admin','admin_demo@rodamar.example',1,1,'2026-11-05 16:39:49.017273'),(2,'pbkdf2_sha256$1000000$uPCxp6hodK8sIgKtuqxjsj$SzVyQx+9aFeKqf9suRXdQzs2UfAsRCllSCOyzSS55u0=',NULL,0,'empleado_demo','Esteban','Empleado','empleado_demo@rodamar.example',0,1,'2026-11-05 16:39:49.181603'),(3,'pbkdf2_sha256$1000000$ZoksvQVjXXyShgEaAKhHoh$ALS2C8TToc+vhs6T5HRQukuB9wkb8rf6GCzHns7gCDg=',NULL,0,'empleado2_demo','Paula','Muñoz','empleado2_demo@rodamar.example',0,1,'2026-11-05 16:39:49.341637'),(4,'pbkdf2_sha256$1000000$zk1DSfxPZamMnmkKFLNk2z$VdtxgXXx84lgUv5KINNGa+UWICAvJt/OAB+NwQ11EAY=',NULL,0,'cliente_demo','Carla','Cliente','cliente_demo@rodamar.example',0,1,'2026-11-05 16:39:49.504442'),(5,'pbkdf2_sha256$1000000$EpiYJ9iDIZ3G90jqYtNPo6$lR1+kmS86PdN1DUhkhRPQgJ+I0dHORYj0OSxOyUQYp8=',NULL,0,'cliente_sur_demo','Sergio','Vidal','cliente_sur_demo@rodamar.example',0,1,'2026-11-05 16:39:49.679715'),(6,'pbkdf2_sha256$1000000$zUUKmCw1ZcuoS8xL3hDmR9$w9b3VVSS7zAcaThI2Z0CxlHRG4z8OR4XsvM6/y/nh6w=',NULL,0,'cliente_sinempresa_demo','Nora','Pizarro','cliente_sinempresa_demo@rodamar.example',0,1,'2026-11-05 16:39:49.858995'),(7,'pbkdf2_sha256$1000000$1j073mZ8nyIYZBzGpn27qk$kNnrq4Dn3E1nNPgxWRRyQD4wChhUgFWbrSKB33TkfkQ=',NULL,0,'cliente_pendiente_demo','Iván','Castro','cliente_pendiente_demo@rodamar.example',0,1,'2026-11-05 16:39:50.038217');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (7,2,1),(8,3,1),(9,4,2),(10,5,2),(11,6,2),(12,7,2);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(7,'logistica','buque'),(8,'logistica','camionciguena'),(9,'logistica','cliente'),(11,'logistica','historialestado'),(10,'logistica','vehiculo'),(6,'sessions','session'),(12,'usuarios','perfil'),(13,'usuarios','registroauditoria');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-11-05 16:39:47.853387'),(2,'auth','0001_initial','2026-11-05 16:39:48.012357'),(3,'admin','0001_initial','2026-11-05 16:39:48.054680'),(4,'admin','0002_logentry_remove_auto_add','2026-11-05 16:39:48.059010'),(5,'admin','0003_logentry_add_action_flag_choices','2026-11-05 16:39:48.063519'),(6,'contenttypes','0002_remove_content_type_name','2026-11-05 16:39:48.108484'),(7,'auth','0002_alter_permission_name_max_length','2026-11-05 16:39:48.127220'),(8,'auth','0003_alter_user_email_max_length','2026-11-05 16:39:48.138462'),(9,'auth','0004_alter_user_username_opts','2026-11-05 16:39:48.143628'),(10,'auth','0005_alter_user_last_login_null','2026-11-05 16:39:48.159995'),(11,'auth','0006_require_contenttypes_0002','2026-11-05 16:39:48.160917'),(12,'auth','0007_alter_validators_add_error_messages','2026-11-05 16:39:48.165545'),(13,'auth','0008_alter_user_username_max_length','2026-11-05 16:39:48.188036'),(14,'auth','0009_alter_user_last_name_max_length','2026-11-05 16:39:48.209110'),(15,'auth','0010_alter_group_name_max_length','2026-11-05 16:39:48.218727'),(16,'auth','0011_update_proxy_permissions','2026-11-05 16:39:48.223760'),(17,'auth','0012_alter_user_first_name_max_length','2026-11-05 16:39:48.245092'),(18,'logistica','0001_initial','2026-11-05 16:39:48.335948'),(19,'logistica','0002_proteger_y_historial','2026-11-05 16:39:48.397782'),(20,'logistica','0003_historial_inicial','2026-11-05 16:39:48.405471'),(21,'logistica','0004_validaciones','2026-11-05 16:39:48.433088'),(22,'logistica','0005_normalizar_datos','2026-11-05 16:39:48.442199'),(23,'logistica','0006_reglas_integridad','2026-11-05 16:39:48.456936'),(24,'sessions','0001_initial','2026-11-05 16:39:48.469271'),(25,'usuarios','0001_initial','2026-11-05 16:39:48.575968'),(26,'usuarios','0002_grupos_y_perfiles','2026-11-05 16:39:48.590853'),(27,'usuarios','0003_acciones_seguridad','2026-11-05 16:39:48.598053'),(28,'usuarios','0004_acciones_crud','2026-11-05 16:39:48.604213'),(29,'usuarios','0005_correo_confirmado','2026-11-05 16:39:48.633160');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `logistica_buque` WRITE;
/*!40000 ALTER TABLE `logistica_buque` DISABLE KEYS */;
INSERT INTO `logistica_buque` VALUES (1,'Glovis Stella','V-2026-41','2026-10-02'),(2,'Höegh Trapper','V-2026-44','2026-10-20'),(3,'Morning Celesta','V-2026-47','2026-10-29'),(4,'Auriga Leader','V-2026-52','2026-11-04'),(5,'Grande Santiago','V-2026-55','2026-11-11');
/*!40000 ALTER TABLE `logistica_buque` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `logistica_camionciguena` WRITE;
/*!40000 ALTER TABLE `logistica_camionciguena` DISABLE KEYS */;
INSERT INTO `logistica_camionciguena` VALUES (1,'KXTR-21','Transportes del Pacífico','Pedro Soto','15.432.198-5'),(2,'HJLP-48','Transportes del Pacífico','Marcela Rojas','13.876.540-7'),(3,'WBXD-73','Logística Atacama','Ricardo Araya','16.204.771-K'),(4,'CZ-4471','Cigüeñas del Sur','',NULL);
/*!40000 ALTER TABLE `logistica_camionciguena` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `logistica_cliente` WRITE;
/*!40000 ALTER TABLE `logistica_cliente` DISABLE KEYS */;
INSERT INTO `logistica_cliente` VALUES (1,'Automotriz del Norte SpA','76.123.456-0','+56 2 2345 6789','contacto@autonorte.example'),(2,'Comercial Sur Motors Ltda.','77.654.321-7','+56 2 2987 6543','ventas@surmotors.example'),(3,'Importadora Pacífico S.A.','76.900.123-9','+56 57 241 5500','operaciones@imppacifico.example'),(4,'Andes Vehículos Comerciales SpA','77.310.450-6','+56 55 228 1400','flota@andesvc.example'),(5,'Distribuidora Tamarugal Ltda.','76.458.213-6','+56 57 276 3300','contacto@tamarugal.example'),(6,'Rent a Car Costa Brava SpA','77.888.123-3','','admin@costabrava.example');
/*!40000 ALTER TABLE `logistica_cliente` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `logistica_historialestado` WRITE;
/*!40000 ALTER TABLE `logistica_historialestado` DISABLE KEYS */;
INSERT INTO `logistica_historialestado` VALUES (1,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-10-03 00:39:50.202463',2,1),(2,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 1','Bloque B - Fila 1','empleado_demo','','2026-10-14 08:39:50.202463',2,1),(3,'EN_PROCESO','EN_CAMINO','Bloque B - Fila 1','Bloque B - Fila 1','empleado_demo','','2026-10-25 16:39:50.202463',2,1),(4,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-10-03 01:39:50.202463',3,2),(5,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 2','Despachado','empleado2_demo','','2026-10-11 13:39:50.202463',3,2),(6,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado2_demo','','2026-10-20 01:39:50.202463',3,2),(7,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado2_demo','','2026-10-28 13:39:50.202463',3,2),(8,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-10-03 02:39:50.202463',2,3),(9,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 3','Despachado','empleado_demo','','2026-10-11 14:39:50.202463',2,3),(10,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado_demo','','2026-10-20 02:39:50.202463',2,3),(11,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado_demo','','2026-10-28 14:39:50.202463',2,3),(12,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-10-03 03:39:50.202463',3,4),(13,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 4','Despachado','empleado2_demo','','2026-10-11 15:39:50.202463',3,4),(14,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado2_demo','','2026-10-20 03:39:50.202463',3,4),(15,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado2_demo','','2026-10-28 15:39:50.202463',3,4),(16,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-10-03 04:39:50.202463',2,5),(17,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 1','Despachado','empleado_demo','','2026-10-11 16:39:50.202463',2,5),(18,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado_demo','','2026-10-20 04:39:50.202463',2,5),(19,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado_demo','','2026-10-28 16:39:50.202463',2,5),(20,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-10-03 00:39:50.202463',3,6),(21,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 2','Despachado','empleado2_demo','','2026-10-11 12:39:50.202463',3,6),(22,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado2_demo','','2026-10-20 00:39:50.202463',3,6),(23,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado2_demo','','2026-10-28 12:39:50.202463',3,6),(24,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-10-03 01:39:50.202463',2,7),(25,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 3','Despachado','empleado_demo','','2026-10-11 13:39:50.202463',2,7),(26,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado_demo','','2026-10-20 01:39:50.202463',2,7),(27,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado_demo','','2026-10-28 13:39:50.202463',2,7),(28,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-10-03 02:39:50.202463',3,8),(29,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 4','Despachado','empleado2_demo','','2026-10-11 14:39:50.202463',3,8),(30,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado2_demo','','2026-10-20 02:39:50.202463',3,8),(31,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado2_demo','','2026-10-28 14:39:50.202463',3,8),(32,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-10-03 03:39:50.202463',2,9),(33,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 1','Despachado','empleado_demo','','2026-10-11 15:39:50.202463',2,9),(34,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado_demo','','2026-10-20 03:39:50.202463',2,9),(35,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado_demo','','2026-10-28 15:39:50.202463',2,9),(36,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-10-03 04:39:50.202463',3,10),(37,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 2','Despachado','empleado2_demo','','2026-10-11 16:39:50.202463',3,10),(38,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado2_demo','','2026-10-20 04:39:50.202463',3,10),(39,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado2_demo','','2026-10-28 16:39:50.202463',3,10),(40,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-10-21 00:39:50.202463',2,11),(41,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 3','Bloque A - Fila 2','empleado_demo','','2026-10-29 00:39:50.202463',2,11),(42,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-10-21 01:39:50.202463',3,12),(43,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 4','Bloque B - Fila 6','empleado2_demo','','2026-10-26 09:39:50.202463',3,12),(44,'EN_PROCESO','EN_CAMINO','Bloque B - Fila 6','Bloque B - Fila 6','empleado2_demo','','2026-10-31 17:39:50.202463',3,12),(45,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-10-21 02:39:50.202463',2,13),(46,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 1','Bloque B - Fila 1','empleado_demo','','2026-10-26 10:39:50.202463',2,13),(47,'EN_PROCESO','EN_CAMINO','Bloque B - Fila 1','Bloque B - Fila 1','empleado_demo','','2026-10-31 18:39:50.202463',2,13),(48,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-10-21 03:39:50.202463',3,14),(49,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 2','Despachado','empleado2_demo','','2026-10-25 03:39:50.202463',3,14),(50,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado2_demo','','2026-10-29 03:39:50.202463',3,14),(51,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado2_demo','','2026-11-02 03:39:50.202463',3,14),(52,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-10-21 04:39:50.202463',2,15),(53,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 3','Despachado','empleado_demo','','2026-10-25 04:39:50.202463',2,15),(54,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado_demo','','2026-10-29 04:39:50.202463',2,15),(55,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado_demo','','2026-11-02 04:39:50.202463',2,15),(56,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-10-21 00:39:50.202463',3,16),(57,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 4','Despachado','empleado2_demo','','2026-10-25 00:39:50.202463',3,16),(58,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado2_demo','','2026-10-29 00:39:50.202463',3,16),(59,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado2_demo','','2026-11-02 00:39:50.202463',3,16),(60,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-10-21 01:39:50.202463',2,17),(61,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 1','Bloque A - Fila 8','empleado_demo','','2026-10-29 01:39:50.202463',2,17),(62,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-10-21 02:39:50.202463',3,18),(63,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 2','Bloque A - Fila 9','empleado2_demo','','2026-10-29 02:39:50.202463',3,18),(64,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-10-21 03:39:50.202463',2,19),(65,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 3','Bloque B - Fila 1','empleado_demo','','2026-10-26 11:39:50.202463',2,19),(66,'EN_PROCESO','EN_CAMINO','Bloque B - Fila 1','Bloque B - Fila 1','empleado_demo','','2026-10-31 19:39:50.202463',2,19),(67,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-10-21 04:39:50.202463',3,20),(68,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 4','Despachado','empleado2_demo','','2026-10-25 04:39:50.202463',3,20),(69,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado2_demo','','2026-10-29 04:39:50.202463',3,20),(70,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado2_demo','','2026-11-02 04:39:50.202463',3,20),(71,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-10-21 00:39:50.202463',2,21),(72,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 1','Despachado','empleado_demo','','2026-10-25 00:39:50.202463',2,21),(73,'EN_PROCESO','EN_CAMINO','Despachado','Despachado','empleado_demo','','2026-10-29 00:39:50.202463',2,21),(74,'EN_CAMINO','ENTREGADO','Despachado','Despachado','empleado_demo','','2026-11-02 00:39:50.202463',2,21),(75,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-10-30 01:39:50.202463',3,22),(76,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-10-30 02:39:50.202463',2,23),(77,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 3','Bloque A - Fila 5','empleado_demo','','2026-11-02 14:39:50.202463',2,23),(78,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-10-30 03:39:50.202463',3,24),(79,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 4','Bloque A - Fila 6','empleado2_demo','','2026-11-02 15:39:50.202463',3,24),(80,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-10-30 04:39:50.202463',2,25),(81,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 1','Bloque A - Fila 7','empleado_demo','','2026-11-02 16:39:50.202463',2,25),(82,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-10-30 00:39:50.202463',3,26),(83,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 2','Bloque B - Fila 2','empleado2_demo','','2026-11-01 08:39:50.202463',3,26),(84,'EN_PROCESO','EN_CAMINO','Bloque B - Fila 2','Bloque B - Fila 2','empleado2_demo','','2026-11-03 16:39:50.202463',3,26),(85,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-10-30 01:39:50.202463',2,27),(86,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-10-30 02:39:50.202463',3,28),(87,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-10-30 03:39:50.202463',2,29),(88,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 1','Bloque A - Fila 2','empleado_demo','','2026-11-02 15:39:50.202463',2,29),(89,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-10-30 04:39:50.202463',3,30),(90,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 2','Bloque A - Fila 3','empleado2_demo','','2026-11-02 16:39:50.202463',3,30),(91,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-11-05 00:39:50.202463',2,31),(92,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-11-05 01:39:50.202463',3,32),(93,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-11-05 02:39:50.202463',2,33),(94,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-11-05 03:39:50.202463',3,34),(95,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-11-05 04:39:50.202463',2,35),(96,'ENCONTRADO','EN_PROCESO','Muelle Norte - Zona 3','Bloque A - Fila 8','empleado_demo','','2026-11-05 16:39:50.202463',2,35),(97,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-11-05 00:39:50.202463',3,36),(98,'','ENCONTRADO','','Muelle Norte - Zona 1','empleado_demo','Ingreso al manifiesto','2026-11-05 01:39:50.202463',2,37),(99,'','ENCONTRADO','','Muelle Norte - Zona 2','empleado2_demo','Ingreso al manifiesto','2026-11-05 02:39:50.202463',3,38),(100,'','ENCONTRADO','','Muelle Norte - Zona 3','empleado_demo','Ingreso al manifiesto','2026-11-05 03:39:50.202463',2,39),(101,'','ENCONTRADO','','Muelle Norte - Zona 4','empleado2_demo','Ingreso al manifiesto','2026-11-05 04:39:50.202463',3,40);
/*!40000 ALTER TABLE `logistica_historialestado` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `logistica_vehiculo` WRITE;
/*!40000 ALTER TABLE `logistica_vehiculo` DISABLE KEYS */;
INSERT INTO `logistica_vehiculo` VALUES (1,'JTDKB20U093456781','Toyota','Hilux','Blanco','Bloque B - Fila 1','EN_CAMINO','2026-10-03 00:39:50.202463',1,1,1),(2,'KMHRDM70000000001','Hyundai','Tucson','Gris','Despachado','ENTREGADO','2026-10-03 01:39:50.202463',1,2,1),(3,'3N1RDM70000000002','Nissan','Versa','Rojo','Despachado','ENTREGADO','2026-10-03 02:39:50.202463',1,3,1),(4,'MA3RDM70000000003','Suzuki','Swift','Azul','Despachado','ENTREGADO','2026-10-03 03:39:50.202463',1,4,1),(5,'LGXRDM70000000004','BYD','Dolphin','Negro','Despachado','ENTREGADO','2026-10-03 04:39:50.202463',1,1,1),(6,'KNARDM70000000005','Kia','Sportage','Plata','Despachado','ENTREGADO','2026-10-03 00:39:50.202463',1,2,1),(7,'LSGRDM70000000006','Chevrolet','Sail','Verde','Despachado','ENTREGADO','2026-10-03 01:39:50.202463',1,3,3),(8,'LSJRDM70000000007','MG','ZS','Blanco','Despachado','ENTREGADO','2026-10-03 02:39:50.202463',1,4,3),(9,'JM1RDM70000000008','Mazda','CX-5','Gris','Despachado','ENTREGADO','2026-10-03 03:39:50.202463',1,1,3),(10,'JTDRDM70000000009','Toyota','Hilux','Rojo','Despachado','ENTREGADO','2026-10-03 04:39:50.202463',1,2,3),(11,'KMHRDM70000000010','Hyundai','Tucson','Azul','Bloque A - Fila 2','EN_PROCESO','2026-10-21 00:39:50.202463',2,NULL,2),(12,'3N1RDM70000000011','Nissan','Versa','Negro','Bloque B - Fila 6','EN_CAMINO','2026-10-21 01:39:50.202463',2,4,2),(13,'MA3RDM70000000012','Suzuki','Swift','Plata','Bloque B - Fila 1','EN_CAMINO','2026-10-21 02:39:50.202463',2,1,2),(14,'LGXRDM70000000013','BYD','Dolphin','Verde','Despachado','ENTREGADO','2026-10-21 03:39:50.202463',2,2,2),(15,'KNARDM70000000014','Kia','Sportage','Blanco','Despachado','ENTREGADO','2026-10-21 04:39:50.202463',2,3,2),(16,'LSGRDM70000000015','Chevrolet','Sail','Gris','Despachado','ENTREGADO','2026-10-21 00:39:50.202463',2,4,2),(17,'LSJRDM70000000016','MG','ZS','Rojo','Bloque A - Fila 8','EN_PROCESO','2026-10-21 01:39:50.202463',2,NULL,4),(18,'JM1RDM70000000017','Mazda','CX-5','Azul','Bloque A - Fila 9','EN_PROCESO','2026-10-21 02:39:50.202463',2,NULL,4),(19,'JTDRDM70000000018','Toyota','Hilux','Negro','Bloque B - Fila 1','EN_CAMINO','2026-10-21 03:39:50.202463',2,3,4),(20,'KMHRDM70000000019','Hyundai','Tucson','Plata','Despachado','ENTREGADO','2026-10-21 04:39:50.202463',2,4,4),(21,'3N1RDM70000000020','Nissan','Versa','Verde','Despachado','ENTREGADO','2026-10-21 00:39:50.202463',2,1,4),(22,'MA3RDM70000000021','Suzuki','Swift','Blanco','Muelle Norte - Zona 2','ENCONTRADO','2026-10-30 01:39:50.202463',3,NULL,1),(23,'LGXRDM70000000022','BYD','Dolphin','Gris','Bloque A - Fila 5','EN_PROCESO','2026-10-30 02:39:50.202463',3,NULL,1),(24,'KNARDM70000000023','Kia','Sportage','Rojo','Bloque A - Fila 6','EN_PROCESO','2026-10-30 03:39:50.202463',3,NULL,1),(25,'LSGRDM70000000024','Chevrolet','Sail','Azul','Bloque A - Fila 7','EN_PROCESO','2026-10-30 04:39:50.202463',3,NULL,1),(26,'LSJRDM70000000025','MG','ZS','Negro','Bloque B - Fila 2','EN_CAMINO','2026-10-30 00:39:50.202463',3,2,1),(27,'JM1RDM70000000026','Mazda','CX-5','Plata','Muelle Norte - Zona 3','ENCONTRADO','2026-10-30 01:39:50.202463',3,NULL,5),(28,'JTDRDM70000000027','Toyota','Hilux','Verde','Muelle Norte - Zona 4','ENCONTRADO','2026-10-30 02:39:50.202463',3,NULL,5),(29,'KMHRDM70000000028','Hyundai','Tucson','Blanco','Bloque A - Fila 2','EN_PROCESO','2026-10-30 03:39:50.202463',3,NULL,5),(30,'3N1RDM70000000029','Nissan','Versa','Gris','Bloque A - Fila 3','EN_PROCESO','2026-10-30 04:39:50.202463',3,NULL,5),(31,'MA3RDM70000000030','Suzuki','Swift','Rojo','Muelle Norte - Zona 3','ENCONTRADO','2026-11-05 00:39:50.202463',4,NULL,2),(32,'LGXRDM70000000031','BYD','Dolphin','Azul','Muelle Norte - Zona 4','ENCONTRADO','2026-11-05 01:39:50.202463',4,NULL,2),(33,'KNARDM70000000032','Kia','Sportage','Negro','Muelle Norte - Zona 1','ENCONTRADO','2026-11-05 02:39:50.202463',4,NULL,2),(34,'LSGRDM70000000033','Chevrolet','Sail','Plata','Muelle Norte - Zona 2','ENCONTRADO','2026-11-05 03:39:50.202463',4,NULL,2),(35,'LSJRDM70000000034','MG','ZS','Verde','Bloque A - Fila 8','EN_PROCESO','2026-11-05 04:39:50.202463',4,NULL,2),(36,'JM1RDM70000000035','Mazda','CX-5','Blanco','Muelle Norte - Zona 4','ENCONTRADO','2026-11-05 00:39:50.202463',4,NULL,3),(37,'JTDRDM70000000036','Toyota','Hilux','Gris','Muelle Norte - Zona 1','ENCONTRADO','2026-11-05 01:39:50.202463',4,NULL,3),(38,'KMHRDM70000000037','Hyundai','Tucson','Rojo','Muelle Norte - Zona 2','ENCONTRADO','2026-11-05 02:39:50.202463',4,NULL,3),(39,'3N1RDM70000000038','Nissan','Versa','Azul','Muelle Norte - Zona 3','ENCONTRADO','2026-11-05 03:39:50.202463',4,NULL,3),(40,'MA3RDM70000000039','Suzuki','Swift','Negro','Muelle Norte - Zona 4','ENCONTRADO','2026-11-05 04:39:50.202463',4,NULL,3);
/*!40000 ALTER TABLE `logistica_vehiculo` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `usuarios_perfil` WRITE;
/*!40000 ALTER TABLE `usuarios_perfil` DISABLE KEYS */;
INSERT INTO `usuarios_perfil` VALUES (1,'+56 9 5555 1001',NULL,1,1),(2,'+56 9 5555 1002',NULL,2,1),(3,'+56 9 5555 1003',NULL,3,1),(4,'+56 9 5555 1004',1,4,1),(5,'+56 9 5555 1005',2,5,1),(6,'+56 9 5555 1006',NULL,6,1),(7,'+56 9 5555 1007',NULL,7,0);
/*!40000 ALTER TABLE `usuarios_perfil` ENABLE KEYS */;
UNLOCK TABLES;

LOCK TABLES `usuarios_registroauditoria` WRITE;
/*!40000 ALTER TABLE `usuarios_registroauditoria` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios_registroauditoria` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

