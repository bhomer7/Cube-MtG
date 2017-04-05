#!/usr/bin/env python3
"""
Update the full files for each rarity.
"""
import glob


def main(rarity_file='rarities.yaml'):
    """
    Create full files for each rarity.
    """
    for rarity in glob.glob('*s/'):
        lines = []
        for rare_file in glob.glob('{}*.dec'.format(rarity)):
            with open(rare_file) as rfile:
                lines += list(rfile.readlines())
        if len(lines) > 0:
            with open('{}.dec'.format(rarity[:-1]), 'w') as out_file:
                out_file.write(''.join(lines))


if __name__ == '__main__':
    main()
