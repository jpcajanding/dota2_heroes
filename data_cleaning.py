import requests
import numpy as np
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

# these datasets are for classification
patch45_heroes.to_pickle('data\pro_heroes_patch_45.pkl')
patch46_heroes.to_pickle('data\pro_heroes_patch_46.pkl')

heroes = requests.get('https://api.opendota.com/api/heroes').json()
heroes = pd.DataFrame.from_dict(heroes)


def parse_hero_names(patch_heroes, heroes):
    hero_names = pd.DataFrame([])

    for column_name in patch_heroes.columns:
        if ('win' in column_name or 'loss' in column_name):
            hero_names[column_name + '_name'] = patch_heroes.merge(heroes, how='left', left_on=column_name, right_on='id')['localized_name']

    hero_names.drop(columns='radiant_win_name', inplace=True)

    return hero_names


hero_names_45 = parse_hero_names(patch45_heroes, heroes)
hero_names_46 = parse_hero_names(patch46_heroes, heroes)

hero_names_45.to_csv('data\hero_names_45.csv')
hero_names_46.to_csv('data\hero_names_46.csv')


def get_hero_cross_tabulation(hero_match_results, heroes):
    win_columns = [column for column in hero_names_45.columns if 'win' in column]
    loss_columns = [column for column in hero_names_45.columns if 'loss' in column]

    heroes['losses'] = heroes['localized_name'].map(hero_match_results[loss_columns].melt()['value'].value_counts())
    heroes['wins'] = heroes['localized_name'].map(hero_match_results[win_columns].melt()['value'].value_counts())
    heroes['picks'] = heroes['localized_name'].map(hero_match_results.melt()['value'].value_counts())

    for hero in heroes['localized_name']:
        hero_lost_matches = hero_match_results[(hero_match_results[loss_columns].values == hero).any(1)]
        heroes['win_against_' + hero] = heroes['localized_name'].map(hero_lost_matches[win_columns].melt()['value'].value_counts())
        heroes['loss_with_' + hero] = heroes['localized_name'].map(hero_lost_matches[loss_columns].melt()['value'].value_counts())
        hero_won_matches = hero_match_results[(hero_match_results[win_columns].values == hero).any(1)]
        heroes['win_with_' + hero] = heroes['localized_name'].map(hero_lost_matches[win_columns].melt()['value'].value_counts())
        heroes['loss_against_' + hero] = heroes['localized_name'].map(hero_lost_matches[loss_columns].melt()['value'].value_counts())

    return heroes


heroes_p45 = get_hero_cross_tabulation(hero_names_45, heroes)
heroes_p46 = get_hero_cross_tabulation(hero_names_46, heroes)

print(heroes_p45.shape)
print(heroes_p46.shape)

heroes_p45.to_csv('data\heroes_patch_45.csv')
heroes_p46.to_csv('data\heroes_patch_46.csv')