# CSC716 PROJECT TOPIC#1: CPU SCHEDULING ALGORITHMS COMPARISON
# Team: Zehui Wen, Meng Meng, Dylan Contractor

# Main class, program run start from here!

import os
import datetime
from Scheduler import Scheduler
import ProcessGen

# Constant file paths
CWD = os.getcwd()
DEFAULT_LOG_DIR = "{cwd}\\Logs".format(cwd=CWD)
DEFAULT_DATA_DIR = "{cwd}\\Dataset".format(cwd=CWD)

# Bool to control program run state
isRun = True
# Custom path to save a output log
logPath = DEFAULT_LOG_DIR

# Command function to exit program
def exit(txt):
    global isRun
    isRun = False

def gen(txt):
    fileName = ""
    try:
        fileName = txt.split(" ")[1]
    except IndexError:
        pass
    ProcessGen.gen(fileName)

# Command function to check dataset files currently in the dataset folder
def ls(txt):
    datasetList = os.listdir(DEFAULT_DATA_DIR)
    if len(datasetList) > 0:
        for file in datasetList:
            print(file)
    else:
        print("Dataset folder is empty.")

# Command function to run the "sim" command, which to start a simulation
def sim(txt):
    # Constant variables
    # Flag list
    SIM_FLAG_LIST = ["-d", "-v", "-a"]
    # Algorthim list
    ALGORITHM_LIST = ["fcfs", "sjf", "srtn", "rr"]
    # Constant Variables
    ALGORITHM = 0
    QUANTUM_TIME = 1
    global logPath
    # Split input text by "<" to separate as command text and file path
    txtEle = txt.split("<")
    # If splited text length is not 2, then command is invalid
    if(len(txtEle) != 2):
        print("Error: Invalid Command, Missing \"<\" symbol, Simulation Aborted.")
    # If splited text length is 2, then get command text and file path
    else:
        cmd, filePath = txtEle[0].lower(), txtEle[1].replace(" ", "")
        # Split command text into array with flags
        flags = cmd.split(" ")
        # Command related variables
        isCmdInvalid = False
        isDetailedMode = False
        isVerboseMode = False
        selectedAlgorithms = []
        #remove extra spaces in flags
        flags = [i for i in flags if i != '']
        # Read flags
        l = len(flags)
        i = 1
        while i < l and not isCmdInvalid:
            flag = flags[i]
            if(flag == "-d"):
                isDetailedMode = True
            elif(flag == "-v"):
                isVerboseMode = True
            elif(flag == "-a"):
                # while i is not the last element in flags, check next element
                while(i != l - 1):
                    i += 1
                    curAlogrithm = flags[i]
                    quantumTime = 0 
                    # If the next element is an algorithm name, then set selected algorithm
                    if(curAlogrithm in ALGORITHM_LIST):
                        # If the selected algorithm is round robin, then set quantum time
                        if(curAlogrithm == "rr" and i + 1 != l):
                            i += 1
                            if flags[i].isnumeric():
                                quantumTime = int(flags[i])
                            else:
                                print("Error: Invalid Quantum Time in index {i} \"{j}\"".format(i=i, j=flags[i]))
                                isCmdInvalid = True
                                break
                        if not isCmdInvalid:
                            selectedAlgorithms.append([curAlogrithm, quantumTime])
                    #else if statement is a flag take one step back (so outer while loop sees flag) and then break
                    elif(curAlogrithm in SIM_FLAG_LIST):
                        i -= 1
                        break
                    else:
                        print("Error: Invalid Algorithm in index {i} \"{j}\"".format(i=i, j=flags[i]))
                        isCmdInvalid = True
                        break
                if len(selectedAlgorithms) == 0:
                    print("Error: No algorithm selected.")
                    isCmdInvalid = True
            else:
                print("Error: Invalid flag in index {i} \"{j}\"".format(i=i, j=flags[i]))
                isCmdInvalid = True
            i += 1
        # If command is valid, start create and run schedulers
        if not isCmdInvalid:
            schedulerList = []
            schedulerName = ""
            id = 1
            # Set Log file name
            logFilePath = "{logPath}\\Output_Log_{timestamp}.txt".format(logPath=logPath, 
                                                                        timestamp=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            # Create a new log file
            logFile = open(logFilePath, "w")
            #if no -a flag set, add algorithms from project description.
            if len(selectedAlgorithms) == 0 :
                selectedAlgorithms = [["fcfs", 0], ["sjf", 0], ["srtn", 0], ['rr', 10], ['rr', 50], ['rr', 100]]
            # Create a scheduler object for each algorithm in list
            for algorithm in selectedAlgorithms:
                if algorithm[ALGORITHM] != "rr":
                    schedulerName = "Scheduler#{id}({algorithm})".format(id=id, algorithm=algorithm[ALGORITHM])
                else:
                    schedulerName = "Scheduler#{id}({algorithm}{quantumTime})".format(id=id, algorithm=algorithm[ALGORITHM], quantumTime=algorithm[QUANTUM_TIME])
                print("Creating scheduler with Name \"{schedulerName}\"".format(schedulerName=schedulerName))
                schedulerList.append(Scheduler(schedulerName, logFile, filePath, isDetailedMode, isVerboseMode, algorithm[ALGORITHM], algorithm[QUANTUM_TIME]))
                id += 1
            # Run simulation for each algorithm
            for scheduler in schedulerList:
                scheduler.runSimulation()
            logFile.close()
            print("Log file has saved in: \"{logFilePath}\""
                  .format(logFilePath=logFilePath))
            print("")
        else:
            print("Simulation Aborted.")

# Function to set a custom output file path
def setLogPath(txt):
    global logPath
    try:
        tempPath = txt.split(" ")[1]
        if os.path.isdir(tempPath):
            logPath = tempPath
            print("New Log file path: {logPath}".format(logPath=logPath))
        else:
            print("Error: This path is not a directory.")
    except IndexError:
        logPath = DEFAULT_LOG_DIR
        print("Reseting to default log file path: {logPath}".format(logPath=DEFAULT_LOG_DIR))

# Function to show help info
def help(txt):
    print("Avaliable Command:")
    print("")
    print("sim [flags] < [input file dir]: Run simulation with specified algorithm. The default input file directory is the Dataset folder, you can simply type the file name without actual directory to open an input file in it.")
    print(" -d: Enable detailed mode, to show all process states before and after simulation.")
    print(" -v: Enable verbose mode, to show cpu action during simulation.")
    print(" -a [algorithm] [quantum time]: Select algorithm (fcfs, sjf, srtn, rr) to run. You can select multiple algorithms at once.")
    print("Example: \"sim -d -v -a rr 10 rr 20 fcfs < data.txt\"")
    print("")
    print("gen [file name]: Generate a random data set file in Dataset folder. If file no name provided, the file will generate as \"#default_process_data.txt\" in default.")
    print("Example: gen data")
    print("")
    print("ls: Show all dataset files currently stored in the dataset folder.")
    print("")
    print("setlogpath [dir]: Change the directory to save the output log files. Use this command without a directory to reset to default directory.")
    print("Example: setlogpath C:\\Users\\admin\\Desktop")
    print("")
    print("exit: Exit the program.")

# Cmd Dict
cmdDict = {
    "exit": exit,
    "gen": gen,
    "ls": ls,
    "sim": sim,
    "setlogpath": setLogPath,
    "help": help
}

# Main function
def main():
    global isRun
    if not os.path.exists(DEFAULT_DATA_DIR):
        os.makedirs(DEFAULT_DATA_DIR)
    if not os.path.exists(DEFAULT_LOG_DIR):
        os.makedirs(DEFAULT_LOG_DIR)
    # Show welcome msg
    print("CSC716 Project Topic #1: SIMULATION: CPU SCHEDULING ALGORITHMS COMPARISON")
    print("Author: Zehui Wen, Meng Meng, Dylan Contractor.")
    print("Version 1.1")
    print("See description.txt or type \"help\" for more information.")
    print("All output log with be saved in \"{logPath}\"".format(logPath=logPath))
    print("")
    try: 
        while isRun:
            # Get input text
            txt = input("$ >> ")
            cmd = txt.split(" ")[0].lower()
            if cmd in cmdDict:
                cmdDict[cmd](txt)
    except KeyboardInterrupt:
        print("\nCtrl-C: Exit.")

main()