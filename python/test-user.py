# Script to create example user to player_stats in Cargogame db

yhteys = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='Cargogame',
    user='pythonuser',  # HUOM käyttäjä: pythonuser
    password='salainen-sana',  # HUOM salasana
    autocommit=True,
    collation='utf8mb3_general_ci'
)
cursor = yhteys.cursor()

cursor.execute('')
