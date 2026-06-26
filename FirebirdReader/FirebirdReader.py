import logging
from logging.handlers import SysLogHandler, NTEventLogHandler
import sys
import time
import os
import platform
from firebird.driver import connect, driver_config

logger = logging.getLogger('firebird_reader')

system = platform.system()

if system == "Linux":
    try:
        syslog_handler = SysLogHandler(address='/dev/log')
        syslog_handler.ident = 'firebird_reader: '
        formatter = logging.Formatter('%(message)s')
        syslog_handler.setFormatter(formatter)
        logger.addHandler(syslog_handler)
        logger.setLevel(logging.INFO)
    except Exception as e:
        print(f"Erreur syslog: {e}")
        
elif system == "Windows":
    handler = NTEventLogHandler('FirebirdReader')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

else:
    logger.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

db_path = os.getenv('FIREBIRD_DB_PATH', 'localhost:EMPLOYEE.FDB')

conn = connect(
    db_path,
    user=os.getenv('FIREBIRD_USER', 'SYSDBA'),
    password=os.getenv('FIREBIRD_PASSWORD', 'admin')
)
cursor = conn.cursor()

def get_all_tables():
    cursor.execute(
        "SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0 AND RDB$VIEW_BLR IS NULL ORDER BY RDB$RELATION_NAME"
    )
    return [row[0].strip() for row in cursor.fetchall()]

def get_first_column(table_name):
    cursor.execute("""
        SELECT FIRST 1 RF.RDB$FIELD_NAME
        FROM RDB$RELATION_FIELDS RF
        WHERE RF.RDB$RELATION_NAME = ?
        ORDER BY RF.RDB$FIELD_POSITION
    """, (table_name,))
    result = cursor.fetchone()
    if result:
        return result[0].strip()
    return None

def FDBFirstread(table_name):
    # 1e lecture de la DB pour récup le contenu déjà présent
    last_id = 0
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY 1")
    for row in cursor.fetchall():
        DataLogging(table_name, row)
        last_id = row[0]
    return last_id

def FDBRead(table_name, last_id):
     #Lecture des nouvelles données d'une table
    conn.commit()
    first_column = get_first_column(table_name)  # ← Assignez d'abord
    try:
        cursor.execute(
            f"SELECT * FROM {table_name} WHERE {first_column} > ? ORDER BY 1",
            (last_id,)
        )
    except Exception as e:
        logger.error(f"Erreur requête {table_name}: {e}")
        return last_id
    
    rows = cursor.fetchall()
    for row in rows:
        DataLogging(table_name, row)
    
    if rows:
        last_id = rows[-1][0]
    return last_id

def DataLogging(table_name, line):
    # Transformation en log
    log = f"[{table_name}] {line}"
    logger.info(log)

last_ids = {}

tables = get_all_tables()
for table_name in tables:
    last_ids[table_name] = FDBFirstread(table_name)

while True:
    for table_name in tables:
        last_ids[table_name] = FDBRead(table_name, last_ids[table_name])
    time.sleep(30)
