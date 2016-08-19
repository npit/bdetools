#!/usr/bin/env bash


commands=
echo "Building keyspace & tables"
cqlsh -e "DROP KEYSPACE IF EXISTS bde;"
cqlsh -f "$commands"
cqlsh -e "DESCRIBE KEYSPACES;"
echo "Built."
echo "Popping into cqlsh again."
cqlsh -k "bde" -e ""