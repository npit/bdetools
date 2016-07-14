#!/usr/bin/env bash

if [ $# -eq 0 ]; then
	name="cluster"
else
	name="$1"
fi

hostmountdir="/home/nik/work/iit/docker/cassandra/mnt"
hostdatadir="/home/npittaras/Documents/project/BDE/clusterData"

dockermountdir="/mnt"
image="cassandra:2.2.4"

datadir=$dockermountdir/data
outdir="$dockermountdir/verify"
configFile="$dockermountdir/cqlshrc"

echo "*************************"
echo "Uploading data"

echo "Importing data. Conf. file : [$configFile]"
for tablename in $(ls $hostdatadir); do
	echo "Pushing to $tablename"
	cp $hostdatadir/$tablename $mountdir/data/$tablename
	#WORKS!
	docker exec $name  cqlsh --cqlshrc "$configFile"  -k "bde" -e "COPY $tablename FROM '$datadir/$tablename'"

	#test does not work : field larger than field limit (131072) @ news articles
	#docker exec $name  cqlsh -k "bde" -e "COPY $tablename FROM '$datadir/$tablename'"

	# config file : 2.2.5 +
	#docker exec $name  cqlsh --cqlshrc "$configFile"  -k "bde" -e "COPY $tablename FROM '$datadir/$tablename' WITH CONFIGFILE='$configFile'"
done