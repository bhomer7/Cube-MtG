# Pack/Pool Descriptions
No pack/pool can generate more than one copy of the same card.

Example pools with them can be found in `pool_results`

## `focusedpool.def`
Creates a 60 card pool with color identity entirely in one shard with 60 cards generated per 'pack'.
* 4 Lands that include the central color of the shard for sure in identity
* 2 Rares that include the central color of the shard for sure in identity
* 2 Rares with 1 contained in each ally pair in the shard
* 12 Uncommons with 6 contained in each ally pair in the shard
* 40 Commons with 10 contained in each ally pair in the shard

## `packwars.def`
Creates a 15 card pack for card wars with no basic lands
* 1 Rares at random with at least 2 colors
* 1 Land at random which has a color identity contained within that of the rare
* 3 Uncommons at random which have a color identity contained within that of the rare
* 10 Commons at random which have a color identity contained within that of the rare

## `rampedpack.def`
Creates a 15 card pack for card wars with no commons.
* 2 Lands at random
* 5 Rares at random
* 8 Uncommons at random

## `random.def`
Creates a 15 card pack with no restrictions except for rarity.
* 1 Land at random
* 1 Rare at random
* 3 Uncommons at random
* 10 Commons at random

## `shardpack.def`
Generates a 15 card pack intended to reprsent spread over a shard(is entirely contained within the shard).
* 1 Land at random with color identity subset of a shard containing primary color or colorless(25% of the time)
* 1 Rare at random with color identity subset of the shard containing primary color or colorless(25% of the time)
* 2 Uncommons at random with color identity a subset of the shard with at least one color
* 1 Uncommon at random that is colorless
* 1 Common at random with color identity equal to the first allied color in the shard
* 1 Common at random with color identity equal to the second allied color in the shard
* 4 Commons at random with color identities equal to the primary color in the shard
* 1 Common at random with color identity equal to the first allied pair in the shard
* 1 Common at random with color identity equal to the second allied pair in the shard
* 1 Common at random with color idenity a subset of the shard
* 1 Common at random that is colorless

## `standardpack.def`
The standard 15 card pack we've found generates a reasonably well balanced cube.
* 1 Land at random
* 1 Rare at random
* 1 Uncommon at random with an ally identity
** Maybe we should make this intersect the Rare
* 1 Uncommon at random with a mono colored or colorless identity
** Maybe we should make this a subset of the ally
* 1 Uncommon at random
* 3 Commons at random from one mono color
** Maybe have sync with Uncommon
* 3 Commons at random from that mono colors ally(clockwise WUBRG)
* 1 Common at random with both of the colors in the allied pair
* 1 Common at random that is colorless
* 2 Commons at random

## `superpool.def`
Creates a 45 card pool entirely with an ally pair.
* 3 Land at random with color idenity contained with an ally pair
* 3 Rares at random with color identity contained within the ally pair
* 9 Uncommons at random with color identity contained within the ally pair
* 30 Commons at random with color identity contained within the ally pair

## `unfocusedpool.def`
Creates a 15 Card pack.
* 1 Land at ranodm
* 1 Rare at random
* 3 Uncommons at random
* 5 Commons at random from each mono color
* 5 Commons at random
