
import MySQLdb,getpass,sys

print
print '*' * 80  
print """
This script will initialize your MySQL server in order to use quota function, 
so you needn\'t  to do it by manual.
"""
print '*' * 80
print


sql = "CREATE DATABASE quota; use quota; CREATE TABLE DB_LIMIT (Db VARCHAR(64)\
 NOT NULL, Max_size BIGINT NOT NULL, Locked TINYINT DEFAULT 0, PRIMARY KEY(Db))\
;CREATE TABLE DB_USERS (User VARCHAR(64) NOT NULL, Db VARCHAR(64) NOT NULL, \
Privilege TINYINT NOT NULL, PRIMARY KEY(Db));"

host = raw_input('MySQL server host(127.0.0.1):')
if not host:
    host = '127.0.0.1'

port = raw_input('MySQL server port(3306):')
if not port:
        port = '3306'
port = int(port)

user = raw_input('Login user(root):')
if not user:
        user = 'root'

password = getpass.getpass('Password:')

conn = MySQLdb.connect(host=host, port=port, user=user, passwd=password)
try:
    cursor = conn.cursor()
    cursor.execute(sql)
except Exception, e:
    print e
    sys.exit(0)

#conn.close()


