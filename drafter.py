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
    total_packs = rarity_config['packs-per-player'] * rarity_config['players']
    packs = [[] for _ in range(total_packs)]

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
        for r in use_rarities:
            random.shuffle(rare_lists[r])

        per_pack = rarity_config[rarity]['per-file']
        for i, pack in enumerate(packs):
            per_pack_with_index = {r: per_pack for r in use_rarities}
            if isinstance(per_pack, list):
                for selections in per_pack:
                    usable = [r for r in selections[3] if len(rare_lists[r]) >= selections[1]]
                    assert len(usable) >= selections[0]
                    random.shuffle(usable)
                    full = usable[:selections[0]]
                    rest = [r for r in selections[3] if r not in full]
                    for r in full:
                        per_pack_with_index[r] = selections[1]
                    for r in rest:
                        per_pack_with_index[r] = selections[2]
            for rare_list in use_rarities:
                the_list = rare_lists[rare_list]
                for _ in range(per_pack_with_index[rare_list]):
                    pack.append(the_list.pop())

        rem_list = []
        for _, lst in rare_lists.items():
            rem_list += lst
        real_per_pack = 0
        if isinstance(per_pack, list):
            for selections in per_pack:
                real_per_pack += selections[0] * selections[1]
                real_per_pack += (len(selections[3]) - selections[0]) * selections[2]
        else:
            real_per_pack = per_pack * len(use_rarities)
        remaining_count = rarity_config[rarity]['total'] - real_per_pack
        random.shuffle(rem_list)
        for pack in packs:
            for _ in range(remaining_count):
                pack.append(rem_list.pop())

    random.shuffle(packs)
    players_with_packs = []
    for i in range(rarity_config['players']):
        player_packs = []
        for j in range(rarity_config['packs-per-player']):
            player_packs.append(packs.pop())
        players_with_packs.append(player_packs)

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
