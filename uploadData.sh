#!/usr/bin/env bash


hostmountdir="$1"
dockermountdir="$2"
hostdatadir="$3"
name="$4"

#hostmountdir="/home/nik/work/iit/docker/cassandra/mnt"
#dockermountdir="/mnt"
#name=""
echo "Uploading data to $name"

dockerdatadir="$dockermountdir/data"
hostmountdatadir="$hostmountdir/data"
dockerConfigFile="$dockermountdir/cqlshrc"

# make data directories on host and container
docker exec $name mkdir -p $dockerdatadir
mkdir -p $hostmountdatadir

echo "*************************"
echo "Uploading data"

echo "Importing data. Conf. file : [$dockerConfigFile]"
for tablename in $(ls $hostdatadir); do
	echo "Pushing to $tablename"
	cp $hostdatadir/$tablename $hostmountdatadir/$tablename
	#WORKS!
	docker exec $name  cqlsh --cqlshrc "$dockerConfigFile"  -k "bde" -e "COPY $tablename FROM '$dockerdatadir/$tablename'"

	#test does not work : field larger than field limit (131072) @ news articles
	#docker exec $name  cqlsh -k "bde" -e "COPY $tablename FROM '$datadir/$tablename'"

	# config file : 2.2.5 +
	#docker exec $name  cqlsh --cqlshrc "$configFile"  -k "bde" -e "COPY $tablename FROM '$datadir/$tablename' WITH CONFIGFILE='$configFile'"
done