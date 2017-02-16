#!/usr/bin/env bash

if [ $# -eq 0 ]; then
	name="cluster"
	portbind="9000"
	ver="2.2.4"
	net="--net=host"
else
	name="$1"
	portbind="$2"
	ver="$3"
	net="$4"
fi
echo "container name : $name"
echo "host port : $portbind"
echo "cassandra version : $ver"


# hostmountdir has to be full path
hostmountdir="$(pwd)/mnt"
mkdir -p  "$hostmountdir"

dockermountdir="/mnt"
#hostdatadir=""  # only relevant if you want to load external data

keyspacebuildcommands="./keyspaceDescr/*"
image="cassandra:$ver" 
hostConfigFile="./cqlshrc"

cp "$hostConfigFile" "$hostmountdir/cqlshrc"
hostConfigFile="$hostmountdir/cqlshrc"
echo "[csv]" > $hostConfigFile
echo "field_size_limit: 500000" >> $hostConfigFile



# run container
cmd=""
cmd+="docker run --name=$name -dit "
cmd+="-v $hostmountdir:$dockermountdir"
cmd+=" $net $image bash"
echo "$cmd"
$cmd


# copy builds commands to mount dir
dockerBuildFolder=$dockermountdir/build_commands
mkdir -p $hostmountdir/build_commands
cp $keyspacebuildcommands $hostmountdir/build_commands/
# add db rebuilding script, useful for debuggery
# and set the correct build dir
cp ./rebuilddb.sh ./rebuild

sed -i "s<CommandsFolder=<CommandsFolder=$dockerBuildFolder<g" ./rebuild
cp ./rebuild $hostmountdir/
# move it to / in the container
docker exec $name mv $dockermountdir/rebuild /rebuild
# remove it from the host
rm ./rebuild


# start cassandra service
cp start.sh $hostmountdir/
echo "Waiting for cqlsh server to get ready."
docker exec $name  $dockermountdir/start.sh
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
echo "Building keyspace & tables"
docker exec $name  cqlsh -e "DROP KEYSPACE IF EXISTS bde;"
echo "Building"
docker exec $name cqlsh -f "$dockerBuildFolder/base"
docker exec $name cqlsh -f "$dockerBuildFolder/news"
docker exec $name cqlsh -f "$dockerBuildFolder/twitter"
docker exec $name cqlsh -f "$dockerBuildFolder/location"
docker exec $name cqlsh -f "$dockerBuildFolder/events"
docker exec $name  cqlsh -e "DESCRIBE KEYSPACES;"
echo "Built."



echo "ip:"
docker inspect --format="{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" $name

# attach terminal, jump to cqlsh
echo "Popping to cqlsh."
docker exec -it $name cqlsh -k "bde" -e "";
# add querying script
cp ./query $hostmountdir/query
docker exec -it $name  cp $dockermountdir/query /query

# to bash
echo "Popping to bash."
docker exec -it $name  bash
