#!/usr/bin/env bash
FILENAME=shardpack
PLAYERS=5
PACKS=5
I=0;
while true;
do
    I=$(($I+1))
    ./packbuilder.py ${FILENAME}.def ${PLAYERS} ${PACKS} && break;
done;
echo $I
