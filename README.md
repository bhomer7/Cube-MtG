A Magic the Gathering Sealed Cube
========================================
Currently this is being built for a 10 person small multiplayer sealed.

Packs are decided by the `.def` file used to create them. There are two included as they should be the most common needed

`pack.def` creates packs suitable for pack wars as each pack will contain at most two colors

`pool.def` is what we use for generating the sealed pools. It creates packs as follows:
- Packs consist of 15 cards
- There will be 1 of each land and rare card in the pool
- There will be 2 of each uncommon in the pool
- There will be 4 of each common in the pool
- There will be 1 Land and 1 Rare
- There will be 3 Uncommons
- There will be 10 Commons
- Rares and Lands will be chosen with no bias
- Uncommons will be chosen with the following requirements on each pack
    * There is at least 1 Ally colored card
    * There is at least 1 Mono colored or Colorless card
- Commons will be chosen with the following requirements on each pack
    * There exist 3 or more cards for each color of an ally pair
    * There exists at least 1 Ally colored card
    * There exists at least 1 Colorless card


Viewing Lists
===========================================
The .dec files can be directly imported into Decked Builder.

Xmage can also import the files.

Building Packs
===========================================
You can build packs automatically with `./packbuilder.py <def file> <num players> <packs per player>`
which will generate the pools for you
