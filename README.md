# fudaff

F.U.D.A. Fantasy Football stats for teams and partner team-ups.

We run 2 leagues so we not only track performance in each league, we also need to match-up the teams across
leagues and keep a running total and ranking.

This script will send some of that to stdout but the main table is emitted in a csv file
suitable for import into Excel or Sheets (import it, don't open it there).

This script relies on the
[espn-api](https://github.com/cwendt94/espn-api)
module, some better
[docs are here](https://github.com/cwendt94/espn-api/wiki/Football-Intro).

# ToDo

*

# Secrets

League specific access details should be provided in a secrets.py file and NOT committed to github.
The following variables should be provided in secrets.py:

* SWID (str)
* LEAGUE1_ID (int)
* ESPN_S2_1 (str)
* LEAGUE2_ID (int)
* ESPN_S2_2 (str)

# Names

We like to include the actual names of the team owners (to help trash taking) so the names.py file
exposes two mappings (per league) of team-id to names as follows (because I don't think espn-api exposes this):

```python
league_2 = {
    "name": "XXX",  # The league name
    "people": {  # id: "name"
        1: "Jane Doe",
        2: "John Doe",
        # etc
    }
}
```

# Installation

Requires at least python 3.7

```bash
pip3 install --upgrade setuptools
pip3 install --upgrade pip
pip3 install --upgrade distlib
pip3 install -r requirements.txt
```

# Execution

```bash
python3 ff.py
```