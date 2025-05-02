# backend.py

from flask import Flask, request, Response, jsonify
import mysql.connector
from flask_cors import CORS

import random
import json
from geopy import distance



app = Flask(__name__)
CORS(app, origins=["http://localhost:63342"])
@app.route("/find-ports")
def find_ports():

    ## TEMPORARY PLANE MODEL
    lentokone_di = {
        "tyyppi": "Lilla Damen 22",
        "kantama": 600,
        "kerroin": 1,
        "hinta": 0,
        "valinnanvara": 4
    }


    sij = request.args["location"]
    suunta = request.args["direction"]
    
    #lentokone_di = request.args["plane-model"]
    kant = lentokone_di["kantama"]
    valvara = lentokone_di["valinnanvara"]

    yhteys = mysql.connector.connect (
        host='127.0.0.1',
        port= 3306,
        database='rahtipeli',
        user='pythonuser',  # HUOM käyttäjä: pythonuser
        password='salainen-sana',  #HUOM salasana
        autocommit=True,
        collation='utf8mb3_general_ci'
        )
    kursori = yhteys.cursor()

    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = f"SELECT latitude_deg, longitude_deg FROM airport where ident = '{sij}'"
    kursori.execute(sql)
    sij_deg = kursori.fetchone()
    # Seuraavaksi haetaan tietokannasta KAIKKIEN kenttien allamerkityt tiedot.
    if lentokone_di["tyyppi"] == "Mamma Birgitta 25":
        sql = (f"SELECT ident, name, type, iso_country, latitude_deg,"
                " longitude_deg FROM airport WHERE type='large_airport'")
    else:
        sql = (f"SELECT ident, name, type, iso_country, latitude_deg,"
                " longitude_deg FROM airport WHERE NOT type='small_airport'")
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
                "id": i + 1,
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
@app.route("/upgrade_airplane_md/<value>", methods=['POST'])

def upgrade_airplane_md(value):
    data = request.get_json()
    value = float(value)
    money = data['money']

    airplane_ar = data['airplane_ar']

    plane_spec = airplane_ar[0]

    airplane_di = {
        "type": plane_spec['type'],
        "distance": plane_spec["distance"],
        "factor": plane_spec["factor"],
        "price": plane_spec["price"],
        "selection": plane_spec["selection"]
    }




    yhteys = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        database='flight_game',
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
                if airplane_di["type"] != value[0]:
                    upgrade = {
                        "airplane_data":{
                            "type": value[0],
                            "distance": value[1],
                            "selection": value[2],
                            "price": value[3],
                            "factor": value[4]
                        },
                        "money_remaining": money-float(value[3])
                    }
                    status = 200
                    return Response(response=json.dumps(upgrade), status=status, mimetype="application/json")
            

        #If you don't have enough money, or you already have this type of plane
        status = 400
        return jsonify({
            "error": "You already have this type of airplane or not enough money",
            "money_remaining": money
        }), status

    #If upgrade value is wrong
    except ValueError:

        status = 400
        return jsonify({
            "error": "Wrong data or value",
            "money_remaining": money
        }), status




if __name__ == "__main__":
    app.run(use_reloader=True, host="127.0.0.1", port=3000)
