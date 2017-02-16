#!/usr/bin/env bash


CommandsFolder=
echo "Building keyspace & tables"
cqlsh -e "DROP KEYSPACE IF EXISTS bde;"
cqlsh -f "$CommandsFolder/base"
cqlsh -f "$CommandsFolder/news"
cqlsh -f "$CommandsFolder/twitter"
cqlsh -f "$CommandsFolder/location"
cqlsh -f "$CommandsFolder/events"

cqlsh -e "DESCRIBE KEYSPACES;"
echo "Built."
echo "Popping into cqlsh again."
cqlsh -k "bde" -e ""