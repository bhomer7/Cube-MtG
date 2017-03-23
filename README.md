A Magic the Gathering Sealed Cube
========================================
Currently this is being built for a 5 person free for all sealed.
Packs consist of 15 cards
There will be 1 of each rare card, 2 of each uncommon, and 4 of each common in
the pool.

Viewing Lists
===========================================
The .dec files can be directly imported into Decked Builder.
Xmage can also import the files.

Building Packs
===========================================
You can build packs automatically with `./drafter.py` which will generate 5 

To build packs manually you
* Deal 1 Random land 
* Deal 1 Random rare 
* Split the uncommons into allies, enemies, and other
    - Deal 1 Random ally 
    - Deal 1 Random other 
    - Deal 1 Random from the uncommons remaining 
* Split the commons into White, Blue, Black, Red, Green, and other
    - Deal 1 Random White 
    - Deal 1 Random Blue 
    - Deal 1 Random Black 
    - Deal 1 Random Red 
    - Deal 1 Random Green 
    - Deal 1 Random Other 
    - Deal 4 Random from the commons remaining 
