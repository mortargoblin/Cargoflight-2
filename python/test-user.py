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

cursor.execute(
    "INSERT INTO player_stats (id, name, money, location, airplane, shifts)"
    "VALUES (0, 'tester', 100000000, 'efhk', 1, 30)"
)
