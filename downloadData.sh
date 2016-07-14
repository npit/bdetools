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
outfoldername="locationExtraction"
outdir="$dockermountdir/$outfoldername"
docker exec $name mkdir -p $outdir
configFile="$dockermountdir/cqlshrc"
echo "Copying to $outdir"

echo "*************************"
echo "Copying data"

for tablename in $(ls $hostdatadir); do
	echo "Pulling to $tablename"

	docker exec $name  cqlsh --cqlshrc "$configFile"  -k "bde" -e "COPY $tablename TO '$outdir/$tablename'"

done