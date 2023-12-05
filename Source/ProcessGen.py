# CSC716 PROJECT TOPIC#1: CPU SCHEDULING ALGORITHMS COMPARISON
# Team: Zehui Wen, Meng Meng, Dylan Contractor

# Prcess Generator
# This is a module file for the process generator
# The procss gen can be called in main with gen command

import os
import random

# Default path to generate input file
DEFAULT_DATA_DIR = "{cwd}\\Dataset\\".format(cwd=os.getcwd())
# Default input file name
DEFAULT_FILE_NAME = "#default_process_data"

def gen(fileName):
    if fileName == "":
        fileName = DEFAULT_FILE_NAME
    filePath = "{defaultDataPath}\\{fileName}.txt".format(defaultDataPath=DEFAULT_DATA_DIR, fileName=fileName)
    f = open(filePath, "w")
    # Generate first line of input file
    processNumber = 50
    switchTime = 5
    f.writelines("{processNumber} {switchTime}\n".format(processNumber=processNumber, switchTime=switchTime))
    # Initial arrival time
    arrivalTime = 0
    # Loop to generate processes
    for processId in range(0, 50):
        # If not the first process(id != 0) than add random number to arrival time
        if processId != 0:
            arrivalTime += random.randint(0, 50)
        burstTime = random.randint(10, 30)
        f.writelines("{processId} {arrivalTime} {burstTime}\n".format(processId=processId, arrivalTime=arrivalTime, burstTime=burstTime))
        # Loop to generate each burst
        for burst in range(0, burstTime):
            CPUTime = random.randint(5, 50)
            IOTime = random.randint(30, 1000)
            if(burst != burstTime - 1):
                f.writelines("{burst} {CPUTime} {IOTime}\n".format(burst=burst, CPUTime=CPUTime, IOTime=IOTime))
            else:
                f.writelines("{burst} {CPUTime}\n".format(burst=burst, CPUTime=CPUTime))
    f.close()
    print("{fileName}.txt has been created".format(fileName=fileName))