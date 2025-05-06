# backend.py

from flask import Flask, request, Response
import mysql.connector
from flask_cors import CORS

import random
import json
from geopy import distance
from numpy.ma.core import masked_not_equal

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

    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = (f"""INSERT INTO player_stats (name, money, airplane, location, shifts) VALUES ('joku', 200000, 1, 'EFHK', 30)"""
           )

    kursori.execute(sql)

##### MOVE TO
@app.route('/move-to/<player>/<icao>')
def move_to(player, icao):

    kursori.execute(
        "UPDATE player_stats "
        f"SET location = '{icao}' "
        f"WHERE name = '{player}' "
    )
    kursori.execute(
        "SELECT location "
        "FROM player_stats "
        f"WHERE name = '{player}' "
    )
    response = kursori.fetchone()
    return str(response[0])

#### FIND PORTS
@app.route("/find-ports")
def find_ports():

    ## TEMPORARY PLANE MODEL
    lentokone_di = {
        "type": "Lilla Damen 22",
        "distance": 800,
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
    
    suunta = request.args["direction"]
    
    #lentokone_di = request.args["plane-model"]
    kant = lentokone_di["distance"]
    valvara = lentokone_di["selection"]

    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = f"SELECT latitude_deg, longitude_deg FROM airport where ident = '{sij}'"
    kursori.execute(sql)
    sij_deg = kursori.fetchone()
    print("airport:", sij)
    print("coordinates:", sij_deg)

    # km to lat/long degrees
    kant_restriction = kant / 90
    print("restriction (deg):", kant_restriction)

    # location limiter
    restricted_lat = (sij_deg[0] - kant_restriction, sij_deg[0] + kant_restriction)
    restricted_long = (sij_deg[1] - kant_restriction, sij_deg[1] + kant_restriction)

    # Seuraavaksi haetaan tietokannasta KAIKKIEN kenttien allamerkityt tiedot.
    if lentokone_di["type"] == "Mamma Birgitta 25":
        sql = (f"SELECT ident, name, type, iso_country, latitude_deg,"
                " longitude_deg FROM airport WHERE type='large_airport'")
    else:
        sql = (
            "SELECT ident, name, type, iso_country, latitude_deg, longitude_deg "
            "FROM airport " 
            "WHERE (type='large_airport' OR type='medium_airport') "
            f"AND latitude_deg > {restricted_lat[0]} AND latitude_deg < {restricted_lat[1]}"
            f"AND longitude_deg > {restricted_long[0]} AND longitude_deg < {restricted_long[1]}"
        )
    kursori.execute(sql)
    airports = kursori.fetchall()

    # Tässä for loop käy jokaikisen lentokentän Euroopasta
    # läpi ja laskee jokaisen kohdalla etäisyyden lähtöpaikasta
    pool = []
    for airport in airports:
        paamaara_deg = (airport[4], airport[5])
        
        # if  
        if (
            distance.distance(sij_deg, paamaara_deg).km < kant 
            and airport[0] != sij
        ):
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
@app.route("/upgrade_airplane/<selection>")
#http://localhost:3000/upgrade_airplane_md?airplane_ar=${airplane_ar}&money=${money}&id=${plane}
def upgrade_airplane(selection):

    selected = float(selection)

    player_stats = ("select player_stats.money, airplane.type "
                    "from airplane, player_stats "
                    "where airplane.id=player_stats.airplane and name='joku'")
    kursori.execute(player_stats)
    stats = kursori.fetchall()

    for stat in stats:
        money = stat[0]
        planetype = stat[1]

    try:
        sql = ("select type, distance, selection, price, factor "
               f"from airplane where id = '{selected}'")
        kursori.execute(sql)
        information = kursori.fetchall()

        for value in information:
            if money >= float(value[3]):
                if planetype != value[0]:
                    new_stats = (f"UPDATE player_stats "
                                 f"SET money='{money-float(value[3])}', airplane='{selected}' "
                                 f"WHERE name='joku'")
                    kursori.execute(new_stats)


                    status = 200
                    message = {"text": "Upgrade has succeed", "money_remaining": money-float(value[3])}
                else:
                    status = 403
                    message = {"text": "You already have this plane.", "money_remaining": money}

            else:
                status = 403
                message = {"text": "You don't have enough money.", "money_remaining": money}

    except ValueError as e:
        message = {"text": str(e),
                   "money_remaining": money
                   }

    return Response(response=json.dumps(message), status=status, mimetype="application/json")


#stat[0]
        #If you don't have enough money, or you already have this type of plane





if __name__ == "__main__":
    app.run(use_reloader=True, host="127.0.0.1", port=3000)
