
MySQL Quota program
===================

# Introduce
This program is used to quota MySQL service. At present, it can be used to limit 
 the execution timeout of queries from users, and the database size. If some 
query does not end before the max time expiring, it will be cancelled by this
program and if the size of some database reached the quota size, it becomes 
unavailable for user to insert data, but remains available for reading.

# Prerequisites
 1. This program was written in Python,  and tested with the version of
2.7.8
 2. MySQLdb module is required, if it was installed in you machine, 
install it before you using it. 

# Run&Usage
 Suggest: Downlaod and run this program in the same host as the MySQL Server 
 which you want to do quota, so that it can run efficiently. 
 1. Get this code in any path
 2. In order to quota some MySQL server, you need to prepare some extra
database and tables. This can be done easily by running the initializeQuota.py.
Keep in mind run this initialize  script only once.
Each time you create a database, config quota info in quota.DB_LIMIT 
table and user info in DB_USERS table.
 3. Run it:
See the help message
$ python mysqlQuota.py  --help
Usage: mysqlQuota [options] 
	   	Options:
        	--help:         print help message
        	--version:      print version of this program
        	--host:         mysql host machine, localhost defaultly
        	--port:         mysql server port, 3306 defaultly
        	--user:         user to login mysql server, root defaultly
        	--password:     user's password, empty defaultly
        	--interval:     interval which is used to check database size quota, default value 60s
        	--timeout:      max executing time for query, default value 5s 

          AlterNatively:
		I present the startup command in a  script start.sh,change 
		param in it,  and run it directly, and call stop.sh to stop. 
