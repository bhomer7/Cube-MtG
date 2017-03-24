#!/usr/bin/env python3
"""
Create packs of cards from the cube in the directory. Can be customized through rarities.yaml.
"""
import glob
import os
import random
import shutil
import yaml

from collections import defaultdict


def rare_index(r):
    """
    Split off the index into the config from a filename.
    """
    return r.split('/')[-1].split('.')[0]


def valid_next_n(lst, ind, n, fun):
    """
    Check if the first n values after an index are valid according to a function. Wraps if needed.
    """
    val = True
    for i in range(n):
        val &= fun(lst[(ind + i) % len(lst)])
    return val


def exist_n_valid(itr, n, fun):
    """
    Check if there exist n values such that they are valid.
    """
    val = 0
    for x in itr:
        if fun(x):
            val += 1
            if val >= n:
                return True
    return False


def main(rarity_file='rarities.yaml'):
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
    dest_dir = rarity_config['dest-dir']
    if os.path.exists('{}'.format(dest_dir)):
        if os.path.exists('{}.bak'.format(dest_dir)):
            print('Deleting {}.bak'.format(dest_dir))
            shutil.rmtree('{}.bak'.format(dest_dir))
        print('Moving {0:} to {0:}.bak'.format(dest_dir))
        shutil.move('{}'.format(dest_dir), '{}.bak'.format(dest_dir))

    for rarity in rarity_config['order']:
        rare_files = glob.glob('{}s/*.dec'.format(rarity))
        rare_count_rem = defaultdict(dict)
        duplication = rarity_config[rarity]['duplication']
        for rare_name in rare_files:
            with open(rare_name) as rare_file:
                cur_line = ''
                comment = True
                for line in rare_file:
                    if comment:
                        cur_line = line
                    else:
                        cur_line += line
                        rare_count_rem[rare_index(rare_name)][cur_line] = duplication
                    comment = not comment
        use_rarities = [r for r in rare_count_rem.keys() if r not in rarity_config[rarity].get('rem-files', [])]

        per_pack = rarity_config[rarity]['per-file']
        for i, pack in enumerate(packs):
            per_pack_with_index = {r: per_pack for r in use_rarities}
            if isinstance(per_pack, list):
                for selections in per_pack:
                    usable = [i for i, _ in enumerate(selections[3]) if
                              valid_next_n(selections[3], i, selections[0],
                                           lambda x: exist_n_valid(rare_count_rem[x].items(), selections[0],
                                           lambda x:x[1] > 0))]
                    assert len(usable) > 0
                    fulli = random.choice(usable)
                    full = [selections[3][(fulli + i) % len(selections[3])] for i in range(selections[0])]
                    rest = [r for r in selections[3] if r not in full]
                    for r in full:
                        per_pack_with_index[r] = selections[1]
                    for r in rest:
                        per_pack_with_index[r] = selections[2]
            for rare_list in use_rarities:
                the_list = [k for k, v in rare_count_rem[rare_list].items() if v > 0]
                assert len(the_list) >= per_pack_with_index[rare_list]
                random.shuffle(the_list)
                for _ in range(per_pack_with_index[rare_list]):
                    card = the_list.pop()
                    pack.append(card)
                    rare_count_rem[rare_list][card] -= 1

        rem_list = []
        for ind, cnt in rare_count_rem.items():
            rem_list += [(ind, c) for c, v in cnt.items() if v > 0]
        real_per_pack = 0
        if isinstance(per_pack, list):
            for selections in per_pack:
                real_per_pack += selections[0] * selections[1]
                real_per_pack += (len(selections[3]) - selections[0]) * selections[2]
        else:
            real_per_pack = per_pack * len(use_rarities)
        remaining_count = rarity_config[rarity]['total'] - real_per_pack
        for pack in packs:
            for _ in range(remaining_count):
                rare_list, card = random.choice(rem_list)
                if card not in pack:
                    pack.append(card)
                    rare_count_rem[rare_list][card] -= 1
                    if rare_count_rem[rare_list][card] == 0:
                        rem_list.remove((rare_list, card))

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
