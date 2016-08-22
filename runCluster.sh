#!/usr/bin/env bash


if [ $# -eq 0 ]; then
	name="cluster"
else
	name="$1"
fi
echo "args $#"
echo "container name : $name"


hostmountdir="/home/nik/work/iit/docker/cassandra/mnt"
dockermountdir="/mnt"
hostdatadir="/home/nik/work/iit/docker/cassandra/data"
keyspacebuildcommands="/home/nik/work/iit/docker/cassandra/cluster_keyspace_build_cmds"
image="cassandra:2.2.4"
hostConfigFile="$hostmountdir/cqlshrc"
echo "[csv]" > $hostConfigFile
echo "field_size_limit: 500000" >> $hostConfigFile

mkdir -p $hostmountdir

# run container
docker run --name=$name -dit \
-p 127.0.0.1:9000:9042 \
-v $hostmountdir:$dockermountdir \
$image


# start cassandra service

echo "Waiting for cqlsh server to get ready."
while [ 1 ]; do
	docker exec $name cqlsh -e "describe keyspaces" > temp 2>&1

	T=$(cat temp | grep system_traces)

	if [ -z "$T" ]; then
		printf "."
		sleep 1
	else
		echo " done!"
		break
	fi
done
rm -f temp

# build db
############
# copy build commands to mount docker dir
cp $keyspacebuildcommands $hostmountdir/keyspacebuildcmds
echo "Building keyspace & tables"
docker exec $name  cqlsh -e "DROP KEYSPACE IF EXISTS bde;"
docker exec $name  cqlsh -f $dockermountdir/keyspacebuildcmds
docker exec $name  cqlsh -e "DESCRIBE KEYSPACES;"
echo "Built."

# import the data

echo "Will not upload any data"
#./uploadData.sh $hostmountdir $dockermountdir $hostdatadir  $name





# attach terminal
docker exec -it $name bash
