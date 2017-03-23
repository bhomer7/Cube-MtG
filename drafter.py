#!/usr/bin/env python3
"""
Create packs of cards from the cube in the directory. Can be customized through rarities.yaml.
"""
import glob
import os
import random
import yaml


def rare_index(r):
    """
    Split off the index into the config from a filename.
    """
    return r.split('/')[-1].split('.')[0]


def main(rarity_file='rarities.yaml', dest_dir='results'):
    """
    Create packs from the rarity file.
    """
    rarity_config = None
    with open(rarity_file) as rarities_file:
        rarity_config = yaml.load(rarities_file)
    if rarity_config is None:
        return
    players_with_packs = [[[] for _ in range(rarity_config['packs-per-player'])]
                          for _ in range(rarity_config['players'])]

    for rarity in rarity_config['order']:
        rare_files = glob.glob('{}s/*.dec'.format(rarity))
        rare_lists = {}
        duplication = rarity_config[rarity]['duplication']
        for rare_name in rare_files:
            with open(rare_name) as rare_file:
                lines = []
                comment = True
                for line in rare_file:
                    if comment:
                        lines.append(line)
                    else:
                        lines[-1] += line
                    comment = not comment
                rare_lists[rare_index(rare_name)] = lines * duplication
        rare_indexes = [rare_index(r) for r in rare_files]
        use_rarities = [r for r in rare_indexes if r not in rarity_config[rarity].get('rem-files', [])]

        rem_list = []
        for rare_list in rarity_config[rarity].get('rem-files', []):
            rem_list += rare_lists[rare_list]

        per_pack = rarity_config[rarity]['per-file']

        for rare_list in use_rarities:
            the_list = rare_lists[rare_list]
            random.shuffle(the_list)
            for player_packs in players_with_packs:
                for player_pack in player_packs:
                    for _ in range(per_pack):
                        player_pack.append(the_list.pop())
            rem_list += the_list

        remaining_count = rarity_config[rarity]['total'] - len(use_rarities) * per_pack
        random.shuffle(rem_list)
        for player_packs in players_with_packs:
            for player_pack in player_packs:
                for _ in range(remaining_count):
                    player_pack.append(rem_list.pop())

    for player_id, player_packs in enumerate(players_with_packs):
        player_pool = []
        directory = '{}/player-{}'.format(dest_dir, player_id + 1)
        if not os.path.exists(directory):
            os.makedirs(directory)
        for pack_id, player_pack in enumerate(player_packs):
            player_pool += player_pack
            with open('{}/pack-{}.dec'.format(directory, pack_id + 1), 'w') as pack_file:
                pack_file.write(''.join(player_pack))

        with open('{}/pool.dec'.format(directory), 'w') as pool_file:
            pool_file.write(''.join(player_pool))


if __name__ == '__main__':
    main()
