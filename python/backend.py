# backend.py
import geopy.distance
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

#This get new stats when you move around
@app.route("/player_stats/<player>")
def player_stats(player):
    sql = (f"select name, money, airplane, location, shifts, type, distance "
           f"from player_stats, airplane "
           f"where player_stats.airplane=airplane.id and name='{player}'")
    kursori.execute(sql)
    data = kursori.fetchall()
    for values in data:
        if values[4] != 0:
            name = {"name": values[0],
                    "money": values[1],
                    "airplane": values[2],
                    "location": values[3],
                    "shifts": values[4],
                    "type": values[5],
                    "distance": values[6],
                    "status": "ok"
                    }
            status = 200
        else:
            status = 200
            name = {"name": values[0],
                    "money": values[1],
                    "airplane": values[2],
                    "location": values[3],
                    "shifts": values[4],
                    "type": values[5],
                    "distance": values[6],
                    "status": "end"
                    }

    return Response(response=json.dumps(name), status=status, mimetype="application/json")

#This minus one from your shifts
@app.route("/shifts_remain/<player>")
def shifts_remain(player):
    sql = (f"select shifts from player_stats where name='{player}'")
    kursori.execute(sql)
    pr_value = kursori.fetchone()[0]

    kursori.execute( "UPDATE player_stats "
        f"SET shifts = '{float(pr_value)-1}' "
        f"WHERE name = '{player}' ")
    return str(pr_value)

#This calculate reward for each airport which findports shows
def reward(tulos, sij_deg, player):
    sqlfact = (f"select factor from airplane, player_stats "
               f"where player_stats.name='{player}' "
               f"and player_stats.airplane=airplane.id")
    kursori.execute(sqlfact)
    factor = kursori.fetchone()[0]

    sqlvisit = f"select ident from visited_country"
    kursori.execute(sqlvisit)
    visited_ident = kursori.fetchall()

    etaisyys = distance.distance((sij_deg[0], sij_deg[1]), (tulos[4], tulos[5])).km
    print(sij_deg[0])
    print(sij_deg[1])
    print(tulos[4])
    print(tulos[5])
    print(etaisyys)

    etaisyys_raha = etaisyys * 2
    country_reward = 1
    country = tulos[3]

    if tulos[2] == "medium_airport":
        base_reward = 2000
    if tulos[2] == "large_airport":
        base_reward = 3500

    match country:
        case "RU" | "BY":
            country_reward = 0.75
        case "FI" | "PL" | "EE" | "HR" | "GR":
            country_reward = 0.95
        case "SE" | "NO" | "DK" | "FR" | "CH" | "SP":
            country_reward = 1.1
        case "GB" | "IT" | "AT":
            country_reward = 1.05
        case "DE" | "LU":
            country_reward = 1.2

    if country in visited_ident:
        base_reward = base_reward / 2



    return (((base_reward * float(factor)) + etaisyys_raha)
            * random.uniform(0.9,1.1) * country_reward)

@app.route("/add_money/<player>/<money>")
def add_money(player, money):

    sql = f"select money from player_stats where name='{player}'"
    kursori.execute(sql)
    oldmoney = kursori.fetchone()[0]
    print(oldmoney)
    kursori.execute(f"UPDATE player_stats SET money='{float(oldmoney)+int(money)}'")

##Create new game and clear previous agme stats
@app.route("/create_new_game/<player>")
def create_new_game(player):
    ## TEMPORARY PLANE MODEL
    sql = (f"")

    # Ensimmäiseksi selvitetään lähtöpaikan sijainti
    sql = (f"""INSERT INTO player_stats (name, money, airplane, location, shifts) VALUES ('{player}', 200000, 1, 'EFHK', 30)"""
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
        "SELECT location, iso_country "
        "FROM player_stats, airport "
        f"WHERE ident=location and player_stats.name = '{player}' "
    )
    response = kursori.fetchone()


    kursori.execute(f"INSERT INTO visited_country (ident) "
                    f"VALUES ('{response[1]}')"
                    )

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
    sql = f"SELECT latitude_deg, longitude_deg, iso_country FROM airport where ident = '{sij}'"
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
            distance.distance((sij_deg[0], sij_deg[1]), paamaara_deg).km < kant
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
                "reward": reward(pool_current, sij_deg, player)
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
@app.route("/upgrade_airplane/<selection>/<player>")
#http://localhost:3000/upgrade_airplane_md?airplane_ar=${airplane_ar}&money=${money}&id=${plane}
def upgrade_airplane(selection, player):

    selected = float(selection)

    player_stats = ("select player_stats.money, airplane.type "
                    "from airplane, player_stats "
                    f"where airplane.id=player_stats.airplane and name='{player}'")
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
                                 f"WHERE name='{player}'")
                    kursori.execute(new_stats)


                    status = 200
                    message = {"text": "Upgrade succeed", "type": value[0], "money_remaining": money-float(value[3])}
                else:
                    status = 403
                    message = {"text": "You already have this plane","type": value[0], "money_remaining": money}

            else:
                status = 403
                message = {"text": "You don't have enough money.", "type": value[0],"money_remaining": money}

    except ValueError as e:
        message = {"text": str(e),
                   "money_remaining": money
                   }

    return Response(response=json.dumps(message), status=status, mimetype="application/json")






if __name__ == "__main__":
    app.run(use_reloader=True, host="127.0.0.1", port=3000)
