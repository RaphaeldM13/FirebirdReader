import logging
from logging.handlers import SysLogHandler
import sys
import fdb

logger = logging.getLogger('firebird_reader')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

syslog_handler = SysLogHandler(address='/dev/log')
syslog_handler.ident = 'firebird_reader: '
logger.addHandler(syslog_handler)

conn = fdb.connect(
    host='localhost',
    user='SYSDBA',
    password='admin',
    database='/opt/FirebirdReader/employee.fdb'
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM EMPLOYEE")


def FDBFirstread():
    # 1e lecture de la DB pour récup le contenu déjà présent
    for row in cursor.fetchall():
        DataLogging(row)

def FDBRead():
    # lecture des nouvelles données de la DB
    line = ["part1","part2","part3"]
    DataLogging(line)

def DataLogging(line):
    # Transformation en log
    log = line
    logger.info(log)

FDBFirstread()
while True :
    FDBRead()
    break
