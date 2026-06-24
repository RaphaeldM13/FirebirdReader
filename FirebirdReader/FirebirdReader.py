import logging

logger = logging.getLogger('firebird_reader')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def FDBFirstread():
    # 1e lecture de la DB pour récup le contenu déjà présent
    print("func1")

def FDBRead():
    # lecture des nouvelles données de la DB
    line = ["part1","part2","part3"]
    DataLogging(line)

def DataLogging(line):
    # Transformation en log
    log = line[0]
    line.pop(0)
    for col in line:
        log += " - " + col
    logger.info(log)

FDBFirstread()
while True :
    FDBRead()
    break