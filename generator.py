# Generate playoff bracket based on team list in db

import sqlite3 as sql
import math

conn = sql.connect("playoffs.db")
cur = conn.cursor()
cur.execute("DELETE FROM match_structure")
cur.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='match_structure'")

#Get team list
teams = cur.execute("SELECT rank,number FROM teams ORDER BY rank").fetchall()
for i in range(len(teams)):
    teams[i] = {"rank": teams[i][0], "number": teams[i][1]}

#Separate teams that skip to primary stage
rounds = 0
while True:
    rounds += 1
    if 2**rounds > len(teams):
        break
rounds -= 1

teams_primary = []
teams_preliminary = []
for i in range(len(teams)):
    if i < len(teams)-((len(teams)-(2**rounds))*2):
        teams_primary.append(teams[i])
    else:
        teams_preliminary.append(teams[i])

#Add primary teams to matches
for team in teams_primary:
    cur.execute("INSERT INTO match_structure (stage,team1,team2,rank_min) VALUES (0,?,?,?)", (team["number"],team["number"],team["rank"]))

#Add preliminary teams to matches
for i in range(int(len(teams_preliminary)/2)):
    team1 = teams_preliminary[i]
    team2 = teams_preliminary[len(teams_preliminary) - i - 1]
    if team2["rank"] < team1["rank"]:
        rank_min = team2["rank"]
    else:
        rank_min = team1["rank"]
    cur.execute("INSERT INTO match_structure (stage,team1,team2,rank_min) VALUES (0,?,?,?)", (team1["number"],team2["number"],rank_min))

#Connect matches together
for stage_target in range(1, rounds + 1):
    source_matches = cur.execute("SELECT id,team1,team2,rank_min FROM match_structure WHERE stage=? ORDER BY rank_min ASC", (stage_target-1,)).fetchall()
    for i in range(len(source_matches)):
        source_matches[i] = {
            "id": source_matches[i][0],
            "team1": source_matches[i][1],
            "team2": source_matches[i][2],
            "rank_min": source_matches[i][3],
        }
    for i in range(int(len(source_matches)/2)):
        match1 = source_matches[i]
        match2 = source_matches[len(source_matches) - i - 1]
        if match1["team1"] == match1["team2"]:
            team1 = match1["team1"]
        else:
            team1 = "w" + str(match1["id"])
        if match2["team1"] == match2["team2"]:
            team2 = match2["team1"]
        else:
            team2 = "w" + str(match2["id"])
        if match2["rank_min"] < match1["rank_min"]:
            rank_min = match2["rank_min"]
        else:
            rank_min = match1["rank_min"]
        cur.execute("INSERT INTO match_structure (stage,team1,team2,rank_min) VALUES (?,?,?,?)", (stage_target,team1,team2,rank_min))

#Remove matches w/ duplicate teams
cur.execute("DELETE FROM match_structure WHERE team1=team2")

#Assign match numbers
highest_match = cur.execute("SELECT COUNT(*) FROM match_structure").fetchall()[0][0]
starting_teams = cur.execute("SELECT team1,team2 FROM match_structure WHERE stage=?", (rounds,)).fetchall()
starting_match_number = int(cur.execute("SELECT value FROM config WHERE key='match_number_start'").fetchall()[0][0]) - 1
cur.execute("UPDATE match_structure SET match_number=? WHERE stage=?", (highest_match+starting_match_number,rounds))

match_number = 1
queue_current = [starting_teams[0][1], starting_teams[0][0]]
queue_building = []
while match_number < highest_match:
    for queue_item in queue_current:
        if queue_item[:1] == "w":
            match_number += 1
            cur.execute("UPDATE match_structure SET match_number=? WHERE id=?",(highest_match-match_number+1+starting_match_number,queue_item[1:]))
            to_add = cur.execute("SELECT team1,team2 FROM match_structure WHERE id=?",(queue_item[1:],)).fetchall()
            queue_building.append(to_add[0][1])
            queue_building.append(to_add[0][0])
    queue_current = queue_building
    queue_building = []

#Assign schedule numbers
tables = int(cur.execute("SELECT value FROM config WHERE key='tables'").fetchall()[0][0])
schedule_number = 0
for stage in range(rounds + 1):
    match_count = cur.execute("SELECT COUNT(match_number) FROM match_structure WHERE stage=?", (stage,)).fetchall()[0][0]
    schedule_number_counts = [0] * math.ceil(match_count / tables)
    i = 0
    while sum(schedule_number_counts) < match_count:
        schedule_number_counts[i] += 1
        i += 1
        if i >= len(schedule_number_counts):
            i = 0
    matches = cur.execute("SELECT match_number FROM match_structure WHERE stage=? ORDER BY match_number", (stage,)).fetchall()
    for i in range(len(matches)):
        matches[i] = matches[i][0]
    i = 0
    for schedule_number_count in schedule_number_counts:
        schedule_number += 1
        for f in range(0, schedule_number_count):
            cur.execute("UPDATE match_structure SET schedule_number=? WHERE match_number=?", (schedule_number,matches[i]))
            i += 1

#Clean up
conn.commit()
conn.close()
print("Created playoff bracket for ", len(teams), " teams (", highest_match, " matches)", sep="")
