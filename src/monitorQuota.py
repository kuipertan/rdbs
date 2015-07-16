
import MySQLdb,time
from excludeUsers import exclude_users

SQL_DB_TAKEN = r'SELECT TABLE_SCHEMA, DATA_LENGTH FROM information_schema.TABLES;'
SQL_DB_LIMIT = r'SELECT * FROM quota.DB_LIMIT;'
SQL_DB_REVOKE = r"UPDATE mysql.db SET Insert_priv='N', Create_priv='N' WHERE Db='"
SQL_DB_LOCK = r"UPDATE quota.DB_LIMIT SET Locked=1 WHERE Db='"
SQL_DB_GRANT = r"UPDATE mysql.db SET Insert_priv='Y', Create_priv='Y' WHERE "
SQL_DB_UNLOCK = r"UPDATE quota.DB_LIMIT SET Locked=0 WHERE Db='"

if len(exclude_users) == 0 :
	excude_users = ('root',)
SQL_EXCLUDE_USERS = "','".join(exclude_users)
SQL_EXCLUDE_USERS = "('" + SQL_EXCLUDE_USERS + "')"

class MySqlQuota:
	def _connect(self):
		slps = 1
		while True:
			try:
				self._conn = MySQLdb.connect(host=self.host, user=self.user, port=self.port, passwd=self.passwd)
			except Exception, e:
				print e
				time.sleep(min(slps, 3600))
				slps *= 3
				continue
			break
		print "Connected to MySQL server " + self.host + ":" + str(self.port)

	def __init__(self, host, port, user, passwd):		
		self.host = host
		self.port = port
		self.user = user
		self.passwd = passwd
		self._connect()
	
	def __del__(self):
		if self._conn:
			self._conn.close()

	def execute(self,*args):pass

class VolumeMonitor(MySqlQuota):	
	def getDbSize(self, taken):
		results = None
		try:
			cursor = self._conn.cursor()
			cursor.execute(SQL_DB_TAKEN)
			results = cursor.fetchall()
		except MySQLdb.OperationalError, e:
			print e
			return -1
		except Exception, e:
			print e
			return -2

		for row in results:
			if row[0] in taken.keys():
				taken[row[0]] += row[1]
			else:
				taken[row[0]] = row[1]
		return 0

	def getDbLimit(self, dbLmt):	
		results = None
		try:
			cursor = self._conn.cursor()
			cursor.execute(SQL_DB_LIMIT)

			results = cursor.fetchall()
		except MySQLdb.OperationalError, e:
			print e
			return -1
		except Exception, e:
			print e
			return -2

		for row in results:
			dbLmt[row[0]] = (row[1],row[2])
		return 0

	def killConnections(self, conds):
		if conds == "":
			return
		cursor = self._conn.cursor()
		results = None
		try:
			cursor.execute("SELECT ID FROM information_schema.processlist where " + conds + ";")
			results = cursor.fetchall()
		except Exception, e:
			print e
			return 
		for row in results:
			cursor.execute("kill " + str(row[0]))
		

	def revokePrivilege(self, dbs):
		if len(dbs) == 0:
			return
		dbs = "' or Db='".join(dbs) + "'"	
		execute = SQL_DB_REVOKE + dbs + ";" + SQL_DB_LOCK + dbs + "; flush privileges;"
		cursor = self._conn.cursor()
		try:
			cursor.execute(execute)
			cursor.close()
		except Exception, e:
			self._conn = None
			print e
			return 
		
	#def checkVolume(self):
	def execute(self, *args):
		st = time.time()
		dbLmt = {}
		if -1 == self.getDbLimit(dbLmt):
			self._conn = None
			return -1
	
		taken = {}
		if -1 == self.getDbSize(taken):
			self._conn = None
			return -1
	
		toRevoke = []
		toGrant = []

		for db in dbLmt.keys():
			if db in taken.keys():
				exausted = taken[db]
				if exausted < dbLmt[db][0] and 1 == dbLmt[db][1]:
					toGrant.append(db)
				if exausted >= dbLmt[db][0] and 0 == dbLmt[db][1]:
					toRevoke.append(db)

		self.revokePrivilege(toRevoke)


		grantConds = ""
		unlock = SQL_DB_UNLOCK +  "' or Db='".join(toGrant) + "'"
		for db in toGrant:
			if grantConds =="":
				grantConds += "(Db='" + db + "' and User in (select User from quota.DB_USERS where Db='" + db + "' and Privilege=0)) ";
			else:
				grantConds += "or (Db='" + db + "' and User in (select User from quota.DB_USERS where Db='" + db + "' and Privilege=0)) ";

		if len(toGrant) > 0:
			execute = SQL_DB_GRANT + grantConds + ";" + unlock +"; flush privileges;" 
			cursor = self._conn.cursor()
			try:
				cursor.execute(execute)
				cursor.close()
			except Exception, e:
				self._conn = None
				print e
				return -1

		revokeThds = ""
		for db in toRevoke:
			if revokeThds =="":
				revokeThds += "(Db='" + db + "' and User in (select User from quota.DB_USERS where Db='" + db + "' and Privilege=0)) ";
			else:
				revokeThds += "or (Db='" + db + "' and User in (select User from quota.DB_USERS where Db='" + db + "' and Privilege=0)) ";

		if grantConds != "" and revokeThds != "":
			self.killConnections(grantConds + " or " +  revokeThds)
		else:
			self.killConnections(grantConds  + revokeThds)
	
		self._conn.commit()
		end = time.time()
		print 'ooooo ' , end-st
		return 0

class ExecutionMonitor(MySqlQuota):
	def setTimeout(self, timeout):
		self._timeout = timeout

	def execute(self, *args):
		if self._conn is None:
			self._connect()
		cursor = self._conn.cursor()
		results = None
		try:
			sql = "SELECT ID FROM information_schema.processlist where COMMAND='Query' and TIME >=" + str(self._timeout) + " and USER NOT IN " + SQL_EXCLUDE_USERS + ";"
			print sql;
			cursor.execute("SELECT ID FROM information_schema.processlist where COMMAND='Query' and TIME >=" + str(self._timeout) + " and USER NOT IN " + SQL_EXCLUDE_USERS + ";")
			#cursor.execute("SELECT ID FROM information_schema.processlist where USER!='root' and COMMAND='Query' and TIME >=" + str(self._timeout) + ";")
			results = cursor.fetchall()
		except Exception, e:
			print e
			self._conn = None
			return -1

		for row in results:
			cursor.execute("kill query " + str(row[0]))
		self._conn.commit()
