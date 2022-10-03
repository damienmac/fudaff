from num2words import num2words
import csv

from espn_api.football import League, Team

from secrets import SWID, LEAGUE1_ID, LEAGUE2_ID, ESPN_S2_1, ESPN_S2_2
from names import LEAGUE1, LEAGUE2

WEEK = 4
YEAR = 2022

# (LEAGUE2 team_id, LEAGUE1 team_id), sorry, backwards.
teammates = [
    (26, 10),
    (23, 9),
    (15, 8),
    (24, 7),
    (22, 6),
    (1, 5),
    (21, 1),
    (25, 4),
    (27, 3),
    (20, 2),
]


class MyTeam:

    def __init__(self, team: Team):
        self.team = team
        self.id = team.team_id

        self.box_scores = []
        self.box_scores_total = 0.0

        self.teammate_id = None
        self.teammate = None
        self.teamup_total_points = None
        self.points_behind = None

    def add_box_score(self, score: float):
        self.box_scores.append(score)
        self.box_scores_total += score

    def add_teammate(self, teammate: 'MyTeam'):
        self.teammate = teammate
        self.teammate_id = teammate.id


def teams_and_standings(league: League):
    print("\nTEAMS & STANDINGS:")
    heading = "standing, team name, tam id, place, wins, losses, ties"

    teams = {}  # keyed off of team_id
    standings = []  # list of csv rows
    team: Team
    for team in league.teams:
        teams[team.team_id] = MyTeam(team)
        place = num2words(team.standing, ordinal=True)
        standings.append(f"{team.standing:02d}, {team.team_name}, {team.team_id}, {place}, {team.wins}, {team.losses}, {team.ties}")

    print(heading)
    [print(row) for row in sorted(standings)]

    return teams


def weekly_matchups(league: League):
    print("\nWEEKLY MATCHUPS")
    for week in range(1, WEEK+1):
        matchups = league.scoreboard(week)
        for matchup in matchups:
            print(f"Week {week}: {matchup.away_team.team_name}({matchup.away_score}) at {matchup.home_team.team_name}({matchup.home_score})")


def weekly_scores(league: League, teams: dict):
    print("\nBOX SCORES BY WEEK")
    scores = {}
    for week in range(1, WEEK+1):
        for box_score in league.box_scores(week):
            home_team = box_score.home_team.team_name
            away_team = box_score.away_team.team_name
            if home_team not in scores.keys():
                scores[home_team] = []
            if away_team not in scores.keys():
                scores[away_team] = []
            scores[home_team].append(str(box_score.home_score))
            scores[away_team].append(str(box_score.away_score))

            home_team_id = box_score.home_team.team_id
            teams[home_team_id].add_box_score(box_score.home_score)

            away_team_id = box_score.away_team.team_id
            teams[away_team_id].add_box_score(box_score.away_score)

    for team in sorted(scores.keys()):
        print(f"{team}, {','.join(scores[team])}")


def summary(league1_name, league_1_teams, league2_name, league_2_teams):
    for pairs in teammates:
        # reminder: it is backwards: LEAGUE2, LEAGUE1
        league_2_teams[pairs[0]].add_teammate(league_1_teams[pairs[1]])
        league_1_teams[pairs[1]].add_teammate(league_2_teams[pairs[0]])

    max_teamup_points = 0.0
    for team_id in league_2_teams.keys():
        team_1 = league_2_teams[team_id].teammate
        team_2 = league_2_teams[team_id]
        total_team_points = team_1.box_scores_total + team_2.box_scores_total
        team_1.teamup_total_points = team_2.teamup_total_points = total_team_points
        if total_team_points > max_teamup_points:
            max_teamup_points = total_team_points

    header = ["Team Up", "Total Team Points", "Points Behind",
              league2_name, f"W-L-T Record ({league2_name})", f"Total Points ({league2_name})",
              league1_name, f"W-L-T Record ({league1_name})", f"Total Points ({league1_name})", ]

    rows = []
    for team_id in league_2_teams:
        team_1 = league_2_teams[team_id].teammate
        team_2 = league_2_teams[team_id]
        team_1.points_behind = team_2.points_behind = (max_teamup_points - team_1.teamup_total_points)

        rows.append({
            "Team Up": f"{team_2.team.team_name} & {team_1.team.team_name}",
            "Total Team Points": team_1.teamup_total_points,
            "Points Behind": team_1.points_behind,
            league2_name: team_2.team.team_name,
            f"W-L-T Record ({league2_name})": f"{team_2.team.wins}-{team_2.team.losses}-{team_2.team.ties}",
            f"Total Points ({league2_name})": team_2.box_scores_total,
            league1_name: team_1.team.team_name,
            f"W-L-T Record ({league1_name})": f"{team_1.team.wins}-{team_1.team.losses}-{team_1.team.ties}",
            f"Total Points ({league1_name})": team_1.box_scores_total
        })

    return header, rows


def league_info():

    # private league with cookies
    league1_name = LEAGUE1["name"]
    league1 = League(league_id=LEAGUE1_ID, year=YEAR, espn_s2=ESPN_S2_1, swid=SWID)

    league2_name = LEAGUE2["name"]
    league2 = League(league_id=LEAGUE2_ID, year=YEAR, espn_s2=ESPN_S2_2, swid=SWID)

    print(f"\n{league1_name}")
    league_1_teams = teams_and_standings(league1)
    # weekly_matchups(league1)
    weekly_scores(league1, league_1_teams)

    print(f"\n{league2_name}")
    league_2_teams = teams_and_standings(league2)
    # weekly_matchups(league2)
    weekly_scores(league2, league_2_teams)

    header, rows = summary(league1_name, league_1_teams, league2_name, league_2_teams)
    print("\n")
    print(header)
    [print(row) for row in rows]

    filename = "fuda-2022.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    league_info()
