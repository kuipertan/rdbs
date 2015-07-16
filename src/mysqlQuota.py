#!/usr/bin/python

"""
/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * author: Kuipertan zhenghai.tan@baifendian.com
 */
"""

import sys,os,threading,getopt,time,signal
from monitorQuota import ExecutionMonitor, VolumeMonitor
from healthyCheck import HealthyCheckServer

host = 'localhost'
port = 3306
user = 'root'
passwd = ''
interval = 60
time_out = 5
schs = []
stoped = False

def usage():
    print 'Usage: mysqlQuota [options] \nOptions:'
    print '\t--help:\t\tprint help message'
    print '\t--version:\tprint version of this program'
    print '\t--host:\t\tmysql host machine, localhost defaultly'
    print '\t--port:\t\tmysql server port, 3306 defaultly'
    print '\t--user:\t\tuser to login mysql server, root defaultly'
    print '\t--password:\tuser\'s password, empty defaultly'
    print '\t--interval:\tinterval which is used to check database size quota, default value 60s'
    print '\t--timeout:\tmax executing time for query, default value 5s'

def version():
    print 'mysqlQuota.py 1.0.0.0'

def siginthandler(signum, frame):
    global stoped
    stoped = True
    stop_all()

signal.signal(signal.SIGINT, siginthandler)

def stop_all():
    for sc in schs:
        sc.cancel()

class ScheduleThread(threading.Thread):
    _name = 'Unnamed'
    def setInterval(self,interval):
        self._interval = interval
    def setTask(self,task):
        self._task = task
    def run(self):
        self.cancel = False
        while not self.cancel:
            self._task.execute()
            time.sleep(self._interval)
    def cancel(self):
        self.cancel = True

def main():
    global schs
    s0 = ScheduleThread()
    s0.setTask(VolumeMonitor(host,port,user,passwd))
    s0.setInterval(interval)
    schs.append(s0)
    s1 = ScheduleThread()
    exm = ExecutionMonitor(host,port,user,passwd)
    exm.setTimeout(time_out)
    s1.setTask(exm)
    s1.setInterval(1)
    schs.append(s1)

    s2 = HealthyCheckServer()
    s2.mysql_info('localhost', 3306, 'sst', 'sst')
    schs.append(s2)
    
    for s in schs:
        s.start()

    while not stoped: 
        time.sleep(5)        

    print "Exit..."
    

if  __name__ == '__main__':
    #pid = os.getpid()
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', 
['help','version','host=', 'port=','user=','password=','interval=','timeout='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        #if o in ('-h', '--help'):
        if o == '--help':
            usage()
            sys.exit(0)
        elif o == '--version':
            version()
            sys.exit(0)
        elif o == '--host':
            host = a
        elif o == '--port':
            if a.isdigit():
                port = int(a)
            else:
                print "--port  digital number is required here"
                sys.exit(1)
        elif o == '--user':
            user = a
        elif o == '--password':
            passwd = a
        elif o == '--interval':
            if a.isdigit():
                interval = int(a)
            else:
                print "--interval  digital number is required here"
                sys.exit(1)
        elif o == '--timeout':
            if a.isdigit():
                time_out = int(a)
            else:
                print "--timeout  digital number is required here"
                sys.exit(1)
    main()
