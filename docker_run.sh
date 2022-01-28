#!/bin/bash

set -a
source .env

cat docker-compose.yml | envsubst | docker-compose $@
