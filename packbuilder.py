#!/usr/bin/env python3
import os
import random
import shutil
import sys

from parsertree import create_tree

DEBUG = False

tree = create_tree(sys.argv[1])
# print(tree)

players = int(sys.argv[2])
packs_per_player = int(sys.argv[3])
dest_dir = 'results'
if len(sys.argv) == 5:
    dest_dir = sys.argv[4]

if os.path.exists('{}'.format(dest_dir)):
    if os.path.exists('{}.bak'.format(dest_dir)):
        print('Deleting {}.bak'.format(dest_dir))
        shutil.rmtree('{}.bak'.format(dest_dir))
    print('Moving {0:} to {0:}.bak'.format(dest_dir))
    shutil.move('{}'.format(dest_dir), '{}.bak'.format(dest_dir))

packs = []
for _ in range(players * packs_per_player):
    pack = []
    tree.eval(pack)
    if DEBUG:
        print(pack)
    packs.append(pack)


random.shuffle(packs)
players_with_packs = []
for i in range(players):
    player_packs = []
    for j in range(packs_per_player):
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
