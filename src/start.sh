#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}

nohup python mysqlQuota.py --host 127.0.0.1 --user dbuser --port 3306 --password dbpass  --timeout 10 &
echo $! > quota.pid
