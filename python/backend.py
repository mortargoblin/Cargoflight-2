# backend.py

from flask import Flask, request, Response
import mysql.connector
from flask_cors import CORS

import random
import json
from geopy import distance

yhteys = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='Cargogame',
    user='pythonuser',  # HUOM käyttäjä: pythonuser
    password='salainen-sana',  # HUOM salasana
    autocommit=True,
    collation='utf8mb3_general_ci'
)
kursori = yhteys.cursor()



app = Flask(__name__)
CORS(app, origins=["http://localhost:63342"])


@app.route("/create_new_game")
def create_new_game():
    ## TEMPORARY PLANE MODEL
    yhteys = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        database='Cargogame',
        user='pythonuser',  # HUOM käyttäjä: pythonuser
        password='salainen-sana',  # HUOM salasana
        autocommit=True,
        collation='utf8mb3_general_ci'
    )
    kursori = yhteys.cursor()

    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = (f"""INSERT INTO player_stats (name, money, airplane, location, shifts) VALUES ('joku', 200000, 1, 'EFHK', 30)"""
           )

    kursori.execute(sql)

##### MOVE TO
@app.route('/move-to/<player>/<icao>')
def move_to(player, icao):
    sql = (
        "UPDATE player_stats "
        f"SET location = '{icao}' "
        f"WHERE name = '{player}' "
        )
    kursori.execute(sql)
    sql = (
        "SELECT location "
        "FROM player_stats "
        f"WHERE name = '{player}' "
    )
    kursori.execute(sql)
    response = kursori.fetchone()
    return str(response[0])

#### FIND PORTS
@app.route("/find-ports")
def find_ports():

    ## TEMPORARY PLANE MODEL
    lentokone_di = {
        "type": "Lilla Damen 22",
        "distance": 600,
        "factor": 1,
        "price": 0,
        "selection": 4
    }

    player = request.args["player"]
    
    kursori.execute(
        "SELECT location FROM player_stats "
        f"WHERE name = '{player}'"
    )

    sij = kursori.fetchone()[0]
    
    print('!!!!!!!!!!!!!!', sij)

    suunta = request.args["direction"]
    
    #lentokone_di = request.args["plane-model"]
    kant = lentokone_di["distance"]
    valvara = lentokone_di["selection"]

    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = f"SELECT latitude_deg, longitude_deg FROM airport where ident = '{sij}'"
    kursori.execute(sql)
    sij_deg = kursori.fetchone()
    # Seuraavaksi haetaan tietokannasta KAIKKIEN kenttien allamerkityt tiedot.
    if lentokone_di["type"] == "Mamma Birgitta 25":
        sql = (f"SELECT ident, name, type, iso_country, latitude_deg,"
                " longitude_deg FROM airport WHERE type='large_airport'")
    else:
        sql = (
            "SELECT ident, name, type, iso_country, latitude_deg, longitude_deg "
            "FROM airport " 
            "WHERE type='large_airport' OR type='medium_airport' "
        )
    kursori.execute(sql)
    airports = kursori.fetchall()

    # Tässä for loop käy jokaikisen lentokentän Euroopasta
    # läpi ja laskee jokaisen kohdalla etäisyyden lähtöpaikasta
    pool = []
    for airport in airports:
        paamaara_deg = (airport[4], airport[5])
        if (distance.distance(sij_deg, paamaara_deg).km < kant and 
        airport[0] != sij and paamaara_deg[1] < 55):
            if suunta=="N": #north
                if paamaara_deg[0] > sij_deg[0]:
                    pool.append(airport)
            elif suunta=="W": #west
                if paamaara_deg[1] < sij_deg[1]:
                    pool.append(airport)
            elif suunta=="S": #south
                if paamaara_deg[0] < sij_deg[0]:
                    pool.append(airport)
            elif suunta=="E": #east
                if paamaara_deg[1] > sij_deg[1]:
                    pool.append(airport)
            else:
                pass

    # Seuraavaksi valitaan lopulliset kandidaatit sattumanvaraisesti
    # Palautettavien määrän määrittää valinnanvara-muuttuja
    tulos = []
    for i in range(int(valvara)):
        try:
            pool_current = random.choice(pool)
            pool.remove(pool_current)

            tulos.append({
                "id": i,
                "ident": pool_current[0],
                "name": pool_current[1],
                "type": pool_current[2],
                "iso_country": pool_current[3],
                "lat": pool_current[4],
                "long": pool_current[5],
            })
            
            status = 200

        except IndexError as ie:
            # Jos kenttiä ei ole riittävästi palautetaan False
            if i + 1 == valvara:
                
                tulos = "Too few airports"
                status = 418

            else:
                # Kumminkin jos kenttiä on tarpeeksi, mutta ei valinnanvaran
                # verran, palautetaan vajaa lista. Näin valinnanvarasta ei
                # tule debuffia.
                pass
            
    return Response(
        response=json.dumps(tulos),
        status=status,
        mimetype="application/json"
    )


#upgrade plane
@app.route("/upgrade_airplane")
#http://localhost:3000/upgrade_airplane_md?airplane_ar=${airplane_ar}&money=${money}&id=${plane}
def upgrade_airplane():

    value = float(request.args.get("id"))
    money = float(request.args.get("money"))

    plane = request.args.get("airplane_ar", [])
    plane_di = json.loads(plane)


    yhteys = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        database='Cargogame',
        user='pythonuser',  # HUOM käyttäjä: pythonuser
        password='salainen-sana',  # HUOM salasana
        autocommit=True,
        collation='utf8mb3_general_ci'
    )
    kursori = yhteys.cursor()


    sql = f"select type, distance, selection, price, factor from airplane where id = '{value}'"
    kursori.execute(sql)
    information = kursori.fetchall()


    try:
        for value in information:
            if money >= float(value[3]):
                if plane_di[0]["type"] != value[0]:
                    print(value[0])

                    upgrade = {
                        "airplane_data":{
                            "type": value[0],
                            "distance": value[1],
                            "selection": value[2],
                            "price": value[3],
                            "factor": value[4]
                        },
                        "money_remaining": money-float(value[3]),
                        "text": "Your upgrade is completed"
                    }
                    status = 200
                else:
                    upgrade = {
                        "airplane_data":{
                            "type": value[0],
                            "distance": value[1],
                            "selection": value[2],
                            "price": value[3],
                            "factor": value[4]
                        },
                        "money_remaining": money,
                        "text": "You already have this plane"}

                    status = 400
            else:
                upgrade = {
                    "airplane_data": {
                        "type": value[0],
                        "distance": value[1],
                        "selection": value[2],
                        "price": value[3],
                        "factor": value[4]
                    },
                    "money_remaining": money,
                    "text": "You don't have enough money."}

                status = 400


    except IndexError as e:
        status = 500
        upgrade = {
            "airplane_data": {

            }
        }

    return Response(response=json.dumps(upgrade), status=status, mimetype="application/json")

        #If you don't have enough money, or you already have this type of plane





if __name__ == "__main__":
    app.run(use_reloader=True, host="127.0.0.1", port=3000)
