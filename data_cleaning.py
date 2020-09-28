import pandas as pd

pro_matches_heroes = pd.read_pickle('data\pro_matches_heroes.pkl')

pro_matches_heroes_patch45 = pro_matches_heroes[pro_matches_heroes['patch'] == 45]
pro_matches_heroes_patch46 = pro_matches_heroes[pro_matches_heroes['patch'] == 46]
del pro_matches_heroes


def parse_heroes(matches, radiant_win, patch):
    heroes = pd.DataFrame([])

    matches.dropna(inplace=True)
    for match in matches['picks_bans']:
        hero = pd.DataFrame(match)

        if radiant_win:
            hero.loc[hero['team'] == 0, 'team'] = 'win'
            hero.loc[hero['team'] == 1, 'team'] = 'loss'
        else:
            hero.loc[hero['team'] == 0, 'team'] = 'loss'
            hero.loc[hero['team'] == 1, 'team'] = 'win'

        picks = hero.loc[hero['is_pick']]
        cols = picks['team'] + '_' + picks.groupby('team').cumcount().add(1).astype(str)
        picks = pd.DataFrame([picks['hero_id'].values], columns=cols).sort_index(1)

        final_hero = {}
        final_hero['match_id'] = hero['match_id']
        final_hero['patch'] = patch
        final_hero['radiant_win'] = radiant_win
        final_hero = pd.DataFrame(data=final_hero, index=[0])
        final_hero = final_hero.join(picks)

        heroes = heroes.append(final_hero, ignore_index=True)
    
    return heroes


patch45_heroes = parse_heroes(pro_matches_heroes_patch45[pro_matches_heroes_patch45['radiant_win']], radiant_win=True, patch=45).append(parse_heroes(pro_matches_heroes_patch45[~pro_matches_heroes_patch45['radiant_win']], radiant_win=False, patch=45), ignore_index=True)
patch46_heroes = parse_heroes(pro_matches_heroes_patch46[pro_matches_heroes_patch46['radiant_win']], radiant_win=True, patch=46).append(parse_heroes(pro_matches_heroes_patch46[~pro_matches_heroes_patch46['radiant_win']], radiant_win=False, patch=46), ignore_index=True)

patch45_heroes.to_pickle('data\pro_heroes_patch_45.pkl')
patch46_heroes.to_pickle('data\pro_heroes_patch_46.pkl')