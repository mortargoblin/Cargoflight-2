# Script to create example user to player_stats in Cargogame db
import mysql.connector

yhteys = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='Cargogame',
    user='pythonuser',
    password='salainen-sana',
    autocommit=True,
    collation='utf8mb3_general_ci'
)
cursor = yhteys.cursor()

cursor.execute("create table visited_country (id int auto_increment primary key, ident varchar(11))")
