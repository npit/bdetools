#!/usr/bin/env bash


if [ $# -eq 0 ]; then
	name="cluster"
	portbind="9000"
else
	name="$1"
	portbind="$2"
fi
echo "container name : $name"
echo "mapped to host port : $portbind"


hostmountdir="$(pwd)/mnt"
dockermountdir="/mnt"
hostdatadir="/home/npittaras/Documents/project/BDE/clusterData"
keyspacebuildcommands="./cluster_keyspace_build_cmds_updatedevents"
image="cassandra:2.2.4"
hostConfigFile="$hostmountdir/cqlshrc"
echo "[csv]" > $hostConfigFile
echo "field_size_limit: 500000" >> $hostConfigFile

mkdir -p $hostmountdir

# run container
docker run --name=$name -dit  \
-p 127.0.0.1:$portbind:9042 \
-v $hostmountdir:$dockermountdir \
$image

# add db rebuilding script, useful for debuggery
cp ./rebuilddb.sh ./rebuild
# set the docker build commands path
sed -i "s<commands=<commands=$dockermountdir/keyspacebuildcmds<g" ./rebuild
cp ./rebuild $hostmountdir/
# move it to / in the container
docker exec $name mv $dockermountdir/rebuild /rebuild
# remove it from the host
rm ./rebuild


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
echo "Not importing data, suspended."
#./uploadData.sh $hostmountdir $dockermountdir $hostdatadir  $name


echo "Will not upload any data"
#./uploadData.sh $hostmountdir $dockermountdir $hostdatadir  $name

#echo "Building twitter_source."
#cp "/home/npittaras/Documents/project/BDE/BDEproject/bde-event-detection-sc7/BDETwitterListener/res/db/cassandra/sample_source_accounts.csv" \
#	$hostmountdir/sourceTwitterAccounts.csv
#docker exec $name  cqlsh -e \
#"COPY bde.twitter_source (account_name, active) FROM '$dockermountdir/sourceTwitterAccounts.csv' WITH HEADER = TRUE AND DELIMITER = '|';";

echo "ip:"
docker inspect --format="{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" $name


# attach terminal
echo "Popping cqlsh."
docker exec -it $name cqlsh -k "bde" -e "";
# to bash
echo "Popping to bash."
docker exec -it $name  bash
