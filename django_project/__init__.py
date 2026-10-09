import pymysql

# Django valida la versión de mysqlclient; con PyMySQL hay que indicarla
pymysql.version_info = (2, 2, 7, "final", 0)
pymysql.install_as_MySQLdb()