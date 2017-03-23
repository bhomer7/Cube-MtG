#!/usr/bin/env python3
"""
Update the full files for each rarity.
"""
import glob
import yaml


def main(rarity_file='rarities.yaml'):
    """
    Create full files for each rarity.
    """
    rarity_config = None
    with open(rarity_file) as rarities_file:
        rarity_config = yaml.load(rarities_file)
    if rarity_config is None:
        return

    for rarity in rarity_config['order']:
        lines = []
        for rare_file in glob.glob('{}s/*.dec'.format(rarity)):
            with open(rare_file) as rfile:
                lines += list(rfile.readlines())
        with open('{}s.dec'.format(rarity), 'w') as out_file:
            out_file.write(''.join(lines))


if __name__ == '__main__':
    main()
