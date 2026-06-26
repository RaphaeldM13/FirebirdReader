import logging
from logging.handlers import SysLogHandler
import sys
import time
from firebird.driver import connect, driver_config

driver_config.server_defaults.host.value = 'localhost'

logger = logging.getLogger('firebird_reader')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# syslog_handler = SysLogHandler(address='/dev/log')
# syslog_handler.ident = 'firebird_reader: '
# logger.addHandler(syslog_handler)

conn = connect(
    "localhost:C:/Program Files/Firebird/Firebird_5_0/examples/empbuild/EMPLOYEE.FDB",
    user='SYSDBA',
    password='admin'
)
cursor = conn.cursor()


def FDBFirstread():
    # 1e lecture de la DB pour récup le contenu déjà présent
    last_emp_no = 0
    cursor.execute("SELECT * FROM EMPLOYEE ORDER BY EMP_NO")
    for row in cursor.fetchall():
        DataLogging(row)
        last_emp_no = row[0]
    return last_emp_no

def FDBRead(last_emp_no):
    # lecture des nouvelles données de la DB
    conn.commit()
    try :
        cursor.execute(
            "SELECT * FROM EMPLOYEE WHERE EMP_NO > ? ORDER BY EMP_NO",
            (last_emp_no,)
        )
    except :
        print("query error")
    rows = cursor.fetchall()
    for row in rows:
        DataLogging(row)
    if rows:
        last_emp_no = rows[-1][0]
    return last_emp_no

def DataLogging(line):
    # Transformation en log
    log = line
    logger.info(log)

last_emp_no = FDBFirstread()
while True :
    last_emp_no = FDBRead(last_emp_no)
