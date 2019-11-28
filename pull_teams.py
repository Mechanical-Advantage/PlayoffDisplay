# Create ranked team list from fllipit db

import sqlite3 as sql

conn_fllipit = sql.connect("..\\FLLScoring2019\\fllipit\\fllipit.db")
cur_fllipit = conn_fllipit.cursor()
conn_playoffs = sql.connect("playoffs.db")
cur_playoffs = conn_playoffs.cursor()

#Get teams and scores from fllipit db
teams = cur_fllipit.execute("SELECT number,round1,round2,round3,round4,round5,round1Penalties,round2Penalties,round3Penalties,round4Penalties,round5Penalties FROM team").fetchall()
teams = [{
    "number": x[0],
    "rounds": [
        {
            "score": x[1],
            "penalties": x[6]
        },
        {
            "score": x[2],
            "penalties": x[7]
        },
        {
            "score": x[3],
            "penalties": x[8]
        },
        {
            "score": x[4],
            "penalties": x[9]
        },
        {
            "score": x[5],
            "penalties": x[10]
        },
    ]
} for x in teams]

#Sort each team's scores
for i in range(len(teams)):
    teams[i]["rounds"].sort(key = lambda x: (-x["score"], x["penalties"]))

#Sort teams by score
def getTuple(x):
    result = ()
    for i in range(5):
        result += (-x["rounds"][i]["score"],)
    for i in range(5):
        result += (x["rounds"][i]["penalties"],)
    return(result)
teams.sort(key = lambda x: getTuple(x))

#Write to playoff db
cur_playoffs.execute("DELETE FROM teams")
for i in range(len(teams)):
    cur_playoffs.execute("INSERT INTO teams(rank,number) VALUES (?,?)", (i+1, teams[i]["number"]))

#Close databases
conn_playoffs.commit()
conn_playoffs.close()
conn_fllipit.close()