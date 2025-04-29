# backend.py

from flask import Flask, request, Response
import mysql.connector

import random
import json
from geopy import distance


app = Flask(__name__)
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




if __name__ == "__main__":
    app.run(use_reloader=True, host="127.0.0.1", port=3000)
