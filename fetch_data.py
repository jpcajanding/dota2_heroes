import json
import time
import requests
import pandas as pd

patch_date_release = 1587052800

teams = requests.get('https://api.opendota.com/api/teams').json()
teams = pd.DataFrame.from_dict(teams)
teams = teams[teams['last_match_time'] >= patch_date_release]

matches = pd.Series([], dtype=int)
team_count = 0

for team in teams['team_id']:
    url = 'https://api.opendota.com/api/teams/' + str(team) + '/matches'
    response = requests.get(url)
    print(team)
    team_matches = response.json()
    team_matches = pd.DataFrame.from_dict(team_matches)
    team_matches = team_matches[team_matches['start_time'] >= patch_date_release]
    matches = matches.append(team_matches['match_id'], ignore_index=True)
    team_count = team_count + 1
    if team_count % 5 == 0:
        matches.drop_duplicates(keep='first', inplace=True)
        print('Saving {0} match ids from {1} teams.'.format(len(matches), team_count))
        matches.to_pickle('data\matches.pkl')
    time.sleep(1)

matches.drop_duplicates(keep='first', inplace=True)

print('Saving {} match ids.'.format(len(matches)))
# matches.to_pickle('data\matches.pkl')
matches = pd.read_pickle('data\matches.pkl')
used_columns = ['match_id', 'radiant_win', 'patch', 'picks_bans']

pro_matches = pd.DataFrame([])
pro_matches_count = 0
err = 0

for match in matches:
    if pro_matches_count <= 109:
        pro_matches_count = pro_matches_count + 1
    else:
        print('requesting match {}'.format(match), flush=True)
        r = requests.get('https://api.opendota.com/api/matches/{}'.format(match))
        pro_match = pd.read_json(r.text, lines=True, orient='columns')

        try:
            pro_match = pro_match[used_columns]
            pro_matches = pro_matches.append(pro_match)
            pro_matches_count = pro_matches_count + 1
            if pro_matches_count % 10 == 0:
                print('Saving {} matches...'.format(pro_matches_count))
                pro_matches.to_pickle('data_new\pro_matches_heroes_110_start.pkl')
        except:
            err = err + 1

        print('Added match {0} of {1}'.format(pro_matches_count, len(matches)))
        time.sleep(1)

print('Total professional matches are {0}. Errors are {1}.'.format(pro_matches_count, err))

print('Saving data for {} matches.'.format(pro_matches_count))
pro_matches.to_pickle('data_new\pro_matches_heroes.pkl')