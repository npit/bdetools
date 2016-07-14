#!/usr/bin/env bash

if [ $# -eq 0 ]; then
	name="cluster"
else
	name="$1"
fi
echo "args $#"
echo "container name : $name"
cp mergedb.py merge.sh builddb_cluster mnt/

mountdir="/home/npittaras/Documents/docker/cassandra/mnt"
dockermountdir="/mnt"
image="cassandra:2.2.4"

# run container
docker run --name=$name -dit \
-p 127.0.0.1:9000:9042 \
-v $mountdir:$dockermountdir \
$image
sleep 1
# start cassandra service
#docker exec $name  service cassandra start
#docker exec $name  service cassandra status
#docker exec $name  service cassandra restart
#sleep 5
#docker exec $name  service cassandra status

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
#docker exec -it $name  bash 

#docker exec -it $name  bash -c $dockermountdir/wait.sh

#docker exec -it $name bash

#docker exec -it $name  watch "cat /var/log/cassandra/system.log | grep 'Starting listening for CQL clients' "
#docker exec -it $name  watch "tail /var/log/cassandra/system.log"

#echo "Paused - check that cassandra's up"
#read -p ""


datadir=$dockermountdir/data
hostdatadir="/home/npittaras/Documents/project/BDE/clusterData"
outdir="$dockermountdir/verify"
docker exec $name mkdir -p $outdir
mkdir -p mnt/data
configFile="$dockermountdir/cqlshrc"

# build db
echo "Building keyspace & tables"
docker exec $name  cqlsh -e "DROP KEYSPACE IF EXISTS bde;"
docker exec $name  cqlsh -f $dockermountdir/builddb_cluster
docker exec $name  cqlsh -e "DESCRIBE KEYSPACES;"
echo "Built."

# import the data

./uploadData.sh





# attach terminal
docker exec -it $name bash
