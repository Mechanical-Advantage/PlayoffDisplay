import sqlite3 as sql
import cherrypy
import json
from pathlib import Path
import sys
import os

#Config
default_port = 8000 # can override w/ command line argument
host = "0.0.0.0"
db_path = "playoffs.db"

if not Path(db_path).is_file():
    print("Creating new database")
    conn = sql.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE teams (
        rank INTEGER NOT NULL,
        number INTEGER NOT NULL UNIQUE,
        name TEXT
        ); """)
    cur.execute("""CREATE TABLE match_structure (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        stage INTEGER NOT NULL,
        match_number INTEGER UNIQUE,
        team1 TEXT NOT NULL,
        team2 TEXT NOT NULL,
        rank_min INTEGER
        ); """)
    cur.execute("""CREATE TABLE match_scores (
        match INTEGER NOT NULL,
        team INTEGER NOT NULL,
        score INTEGER NOT NULL DEFAULT 0,
        penalties INTEGER NOT NULL DEFAULT 0
        ); """)
    conn.commit()
    conn.close()

class main_server(object):
    @cherrypy.expose
    def index(self):
        output = """
<html>
<head>
    <title>
        FLL Playoff Display
    </title>
    <link rel="stylesheet" type="text/css" href="/static/css/index.css"></link>
</head>
<body>
<canvas id="mainCanvas" width=3000 height=1600></canvas>
</body>
<script src="/static/js/index.js"></script>
</html>
            """
        return(output)

    @cherrypy.expose
    def api(self):
        conn = sql.connect(db_path)
        cur = conn.cursor()

        #Get max stage
        max_stage = cur.execute("SELECT MAX(stage) FROM match_structure").fetchall()[0][0]

        #Determine winners
        winners = {}
        max_match = cur.execute("SELECT MAX(match_number) FROM match_structure").fetchall()[0][0]
        for match in range(1, max_match + 1):
            results = cur.execute("SELECT team FROM match_scores WHERE match=? ORDER BY score DESC, penalties ASC, team ASC LIMIT 1", (match,)).fetchall()
            if len(results) > 0:
                winners[match] = results[0][0]

        #Fetch base matches
        matches = cur.execute("SELECT match_number,stage,team1,team2 FROM match_structure ORDER BY match_number").fetchall()
        for i in range(len(matches)):
            matches[i] = {"number": matches[i][0], "stage": matches[i][1], "team1": matches[i][2], "team2": matches[i][3]}

        #Convert to output format
        matches_output = []
        matches_sides = {}
        for match in matches[::-1]:
            output = {"match": match["number"], "inputs": [], "winner": 0}
            
            #Add teams and inputs
            for key in ["team1", "team2"]:
                if match[key][:1] == "w":
                    source_match = cur.execute("SELECT match_number FROM match_structure WHERE id=? LIMIT 1", (match[key][1:],)).fetchall()[0][0]
                    output["inputs"].append(source_match)
                    if source_match in winners:
                        output[key] = str(winners[source_match])
                    else:
                        output[key] = ""
                else:
                    output[key] = str(match[key])
                
                #Get score
                if output[key] != "":
                    score = cur.execute("SELECT score FROM match_scores WHERE match=? AND team=? LIMIT 1", (match["number"], output[key])).fetchall()
                    if len(score) > 0:
                        output[key] += " - " + str(score[0][0]) + " pts"

            #Add winner
            if match["number"] in winners:
                if winners[match["number"]] == int(output["team1"].split(" - ")[0]):
                    output["winner"] = 1
                elif winners[match["number"]] == int(output["team2"].split(" - ")[0]):
                    output["winner"] = 2
                else:
                    output["winner"] = 0

            #Add column
            if match["stage"] == max_stage:
                if len(output["inputs"]) >= 1:
                    matches_sides[output["inputs"][0]] = "left"
                if len(output["inputs"]) >= 2:
                    matches_sides[output["inputs"][1]] = "right"
                output["column"] = 0
            else:
                if matches_sides[match["number"]] == "left":
                    output["column"] = match["stage"] - max_stage
                else:
                    output["column"] = max_stage - match["stage"]
                for i in output["inputs"]:
                    matches_sides[i] = matches_sides[match["number"]]
            
            matches_output.append(output)
                
        conn.close()
        return(json.dumps(matches_output))

if __name__ == "__main__":
    port = default_port
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    cherrypy.config.update({'server.socket_port': port, 'server.socket_host': host})
    cherrypy.quickstart(main_server(), "/", {"/static": {"tools.staticdir.on": True, "tools.staticdir.dir": os.getcwd() + "/static"}})
