import threading, MySQLdb
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from config import healthy_check_server_port as port
mysql_host = 'localhost'
mysql_port = 3306
mysql_user = 'mysql'
mysql_passwd = ''
CHECK_QUERY="SHOW GLOBAL STATUS WHERE variable_name='wsrep_local_state';"

class HealthyCheckHTTPHandler(BaseHTTPRequestHandler):
    def response_OK(self):
        self.send_response(200)
        #self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('MySQL is available.')

    def response_NG(self, error):
        self.send_response(503)
        self.end_headers()
        self.wfile.write('MySQL is unavailable.' + error)

    def check_stat(self):
        conn = None
        error = None
        try:
            conn = MySQLdb.connect(host=mysql_host, port=mysql_port, 
user=mysql_user, passwd=mysql_passwd)
            cursor = conn.cursor()
            cursor.execute(CHECK_QUERY)
        except Exception, e:
            error = str(e)
        if conn:
            conn.close()
        return error


    def do_GET(self):
        error = self.check_stat()
        if self.path == '/state':
            if error:
                self.response_NG(error)
            else:
                self.response_OK()
        else:
            self.response_NG('wrong path')

class HealthyCheckServer(threading.Thread):
    def run(self):
        self._running = True
        server_address = ('', port)
        httpd = HTTPServer(server_address, HealthyCheckHTTPHandler)
        while self._running:
            httpd.handle_request()

    def mysql_info(self, host, port, user, passwd):
        global mysql_host,mysql_port,mysql_user,mysql_passwd
        mysql_host = host
        mysql_port = port
        mysql_user = user
        mysql_passwd = passwd

    def cancel(self):
        self._running = False

if __name__ == '__main__':
    import time
    sv = HealthyCheckServer()
    sv.mysql_info('localhost', 3306, 'sst', 'sst')
    sv.start()
    while True:
        exit = raw_input('exit?y/n:')
        if exit == 'y':
            sv.cancel()
            break
        time.sleep(100)
