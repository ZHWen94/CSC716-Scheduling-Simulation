# CSC716 PROJECT TOPIC#1: CPU SCHEDULING ALGORITHMS COMPARISON
# Team: Zehui Wen, Meng Meng, Dylan Contractor

# Scheduler Module
# This is a class file for the scheduler class
# The scheduler will read the input file and run simulation under selected algorithm

import os
import operator
from Process import Processes
import ProcessGen

# Constant variable for CPU state
CONTEXT_SWITCH = 0
IDLE = 1
WORKING = 2
# Constant file paths
CWD = os.getcwd()
DEFAULT_LOG_DIR = "{cwd}\\Logs".format(cwd=CWD)
DEFAULT_DATA_DIR = "{cwd}\\Dataset".format(cwd=CWD)
DEFAULT_DATA_FILE = "{cwd}\\Dataset\\#default_process_data.txt".format(cwd=CWD)

class Scheduler(object):
    # Consturctor
    def __init__(self, name, logFile, filePath, isDetailedMode, isVerboseMode, selectedAlgorithm, quantumTime):
        # Scheduler name 
        self.name = name
        # Log File to record output
        self.logFile = logFile
        # Algorithm Dict
        self.algorithmDict = {
            "fcfs": self.fcfs,
            "sjf": self.sjf,
            "srtn": self.srtn,
            "rr": self.rr,
        }
        self.algorithmName = {
            "fcfs": "First Come First Serve",
            "sjf": "Shortest Job First",
            "srtn": "Shortest Remaining Time Next",
            "rr": "Roundrobin",
        }
        # Timer for scheduler
        self.idleTime = 0
        self.executeTime = 0
        # Context switch timer and bool
        self.switchTime = 0
        self.curSwitchTime = 0
        self.state = IDLE
        # Ready and finish qeuen
        self.jobList = []
        self.waitList = []
        self.finishedJobList = []
        # The process currently in progress
        self.curJob = None
        # Mode bools
        self.isDetailedMode = isDetailedMode
        self.isVerboseMode = isVerboseMode
        # Algorithm and quantumTime
        self.selectedAlgorithm = selectedAlgorithm
        self.quantumTime = quantumTime
        self.curQuantumTime = quantumTime
        # Read and Input file into job list
        self.readFile(filePath)
        

    # Function to read file into job list, called in constructor
    def readFile(self, filePath):
        # Const variables
        SWITCH_TIME = 1
        PROCESS_ID = 0
        ARRIVAL_TIME = 1
        BURST_TIME = 2
        BURST_NUMBER = 0
        CPU_TIME = 1
        IO_TIME = 2
        # Read file lines
        realPath = self.readFilePath(filePath)
        file = open(realPath)
        fileLines = file.readlines()
        # Create job list
        isFirstLine = True
        isInBurstList = False
        curProcessId = 0
        curBurstNum = 0
        for line in fileLines:
            lineEle = line.split(" ")
            if not isFirstLine:
                if not isInBurstList:
                    curProcessId = int(lineEle[PROCESS_ID])
                    self.jobList.append(Processes(id=curProcessId, arrivalTime=int(lineEle[ARRIVAL_TIME]), burstTime=int(lineEle[BURST_TIME])))
                    isInBurstList = True
                else:
                    curBurstNum = int(lineEle[BURST_NUMBER])
                    if(len(lineEle) == 3):
                        self.jobList[curProcessId].addBurst(burstNum=curBurstNum, CPUTime=int(lineEle[CPU_TIME]), IOTime=int(lineEle[IO_TIME]))
                    elif(len(lineEle) == 2):
                        self.jobList[curProcessId].addBurst(burstNum=curBurstNum, CPUTime=int(lineEle[CPU_TIME]), IOTime=0)
                    curProcess = self.jobList[curProcessId]
                    if curBurstNum == curProcess.getBurstTime() - 1:
                        isInBurstList = False
            else:
                # Set Switch Timer
                self.switchTime = int(lineEle[SWITCH_TIME])
                isFirstLine = False
        file.close()
        # Print message when a scheduler created
        print("{name} has been created sucessfully.".format(name=self.name))

    # Function to read and return a correct file path
    def readFilePath(self, filePath):
        filePath2 = "{defaultDataPath}\\{filePath}".format(defaultDataPath=DEFAULT_DATA_DIR, filePath=filePath)
        if os.path.isfile(filePath):
            return filePath
        elif os.path.isfile(filePath2):
            return filePath2
        else:
            if not os.path.isfile(DEFAULT_DATA_FILE):
                print("{name}: Default data file lost, generating a new dafault data file."
                      .format(name=self.name))
                ProcessGen.gen("")
            print("{name}: Can't read file: \"{filePath}\"".format(name=self.name, filePath=filePath))
            print("{name}: Using default path: \".\\Dataset\\#default_process_data.txt\"".format(name=self.name))
            return DEFAULT_DATA_FILE
    
    # Function to output and save to log
    def log(self, msg):
        print(msg)
        self.logFile.writelines("{msg}\n".format(msg=msg))

    # Function to start the simulation
    def runSimulation(self):
        # Check if error occured in job list
        if len(self.jobList) > 0:
            # Confrim run or not from user
            isConfirmed = False
            while not isConfirmed:
                confirm = input("{name}: Do you want to start the simulation? (Y/N): "
                                .format(name=self.name)).lower()
                if confirm == "y":
                    isConfirmed = True
                    # If is detailed mod, then Show job list
                    if self.isDetailedMode:
                        self.log("Jobs Info: ")
                        self.log("==================================================")
                        for job in self.jobList:
                            job.toString(self.log)
                            self.log("==================================================")
                    if self.isVerboseMode:
                        self.log(self.algorithmName[self.selectedAlgorithm])
                    self.algorithmDict[self.selectedAlgorithm]()
                elif confirm == "n":
                    isConfirmed = True
                    print("{name}: Simulation Aborted.".format(name=self.name))
        else:
            print("Unknown Error: Empty JobList, Simulation Aborted.")

    # Function to check a new job arrive and put into wait list
    def checkJobArrival(self):
        isNewJobArrived = False
        while len(self.jobList) > 0:
            if self.jobList[0].getArrivalTime() == self.executeTime:
                if self.isVerboseMode:
                    self.log("At time unit# {executeTime}: Job# {jobId} arrived, and state in the wait list."
                        .format(executeTime=self.executeTime, jobId=self.jobList[0].getId()))
                self.waitList.append(self.jobList.pop(0))
                isNewJobArrived = True
            if len(self.jobList) <= 0:
                return isNewJobArrived
            elif self.jobList[0].getArrivalTime() != self.executeTime:
                return isNewJobArrived

    # Function to check if cpu is idle and job is in wait list
    def checkAvaiableJob(self):
        if self.state == IDLE and len(self.waitList) > 0:
            if self.isVerboseMode:
                self.log("At time unit {executeTime}: Job# {jobId} moving from wait to execute."
                      .format(executeTime=self.executeTime, jobId=self.waitList[0].getId()))
            self.curJob = self.waitList.pop(0)
            self.state = WORKING

    # Function to check a current job is done
    def chekcCurJobFinish(self):
        if self.state == WORKING and self.curJob.getCurCPUTime() <= 0:
            if self.curJob.goToNextBurst():
                if self.isVerboseMode:
                    self.log("At time unit# {executeTime}: Job# {jobId} finish."
                        .format(executeTime=self.executeTime, jobId=self.curJob.getId()))
                self.finishedJobList.append(self.curJob)
                self.curJob.setFinishTime(self.executeTime)
                self.curJob = None
                self.contextSwitch()
            else:
                if self.isVerboseMode:
                    self.log("At time unit# {executeTime}: Job# {jobId} finish Burst# {burstNum}"
                        .format(executeTime=self.executeTime, jobId=self.curJob.getId(), burstNum=self.curJob.getCurBurstTime()))
                self.waitList.append(self.curJob)
                self.contextSwitch()

    # Function to start a preemtion
    def preemption(self):
        if self.isVerboseMode:
            self.log("At time unit# {executeTime}: Preemption occured, Job# {jobId} move to wait."
                  .format(executeTime=self.executeTime, jobId=self.curJob.getId()))
        self.waitList.append(self.curJob)
        self.curJob = None
        self.contextSwitch()
        pass

    # Function to start a context switch
    def contextSwitch(self):
        if self.isDetailedMode:
            self.log("At time unit# {executeTime}: Context switch occured."
                .format(executeTime=self.executeTime))
        self.curSwitchTime = self.switchTime
        self.state = CONTEXT_SWITCH
    
    def checkContextSwitchFinish(self):
        if self.curSwitchTime <= 0:
            if self.isDetailedMode:
                self.log("At time unit# {executeTime}: Context switch finish."
                        .format(executeTime=self.executeTime))
            self.state = IDLE
            self.curQuantumTime = self.quantumTime

    # Function to check simulation finish
    def isSimFinish(self):
        return self.state == IDLE and len(self.waitList) == 0 and len(self.jobList) == 0
    
    # Function to calculate cpu utilization
    def getCPUUtilization(self):
        return (self.executeTime - self.idleTime) / self.executeTime

    # Scheduling algorithms functions
    # First come first serve
    def fcfs(self):
        print("{name}: Start Simulation...".format(name=self.name))
        print("==================================================")
        while True:
            # Time unit start
            self.checkJobArrival()
            self.checkAvaiableJob()
            # Time unit in-running
            if self.state == IDLE:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: CPU in idle."
                #           .format(executeTime=self.executeTime))
                self.idleTime += 1
            elif self.state == CONTEXT_SWITCH:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: Context switch occuring, remaining time: {curSwitchTime}"
                #           .format(executeTime=self.executeTime, curSwitchTime=self.curSwitchTime))
                self.curSwitchTime -= 1
                self.checkContextSwitchFinish()
            elif self.state == WORKING:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: Job# {jobId} executing in burst# {curBurstTime}: CPU time remain: {CPUTime}"
                #         .format(executeTime=self.executeTime, jobId=self.curJob.getId(), curBurstTime=self.curJob.getCurBurstTime(),
                #                 CPUTime=self.curJob.getCurCPUTime()))
                self.curJob.execute()
            # Time unit end
            self.chekcCurJobFinish()
            if self.isSimFinish():
                if self.isVerboseMode:
                    print("==================================================")
                print("{name}: Simulation Ended.".format(name=self.name))
                break
            self.executeTime += 1
            # if self.isVerboseMode:
            #     self.log("==================================================")
        print("{name}:".format(name=self.name))
        self.log("First Come First Serve:")
        self.log("Total Time required is {executeTime} time units"
              .format(executeTime=self.executeTime))
        self.log("CPU Utilization is {CPUUtilization}"
              .format(CPUUtilization=self.getCPUUtilization()))
        if self.isDetailedMode:
            for job in self.finishedJobList:
                self.log("")
                job.showFinishState(self.log)
        self.log("==================================================")

    # Shortest job first
    def sjf(self):
        print("{name}: Start Simulation...".format(name=self.name))
        print("==================================================")
        while True:
            # Time unit start
            if self.checkJobArrival():
                self.waitList.sort(key=operator.attrgetter('curMaxCPUTime'))
            self.checkAvaiableJob()
            # Time unit running
            if self.state == IDLE:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: CPU in idle."
                #           .format(executeTime=self.executeTime))
                self.idleTime += 1
            elif self.state == CONTEXT_SWITCH:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: Context switch occuring, remaining time: {curSwitchTime}"
                #           .format(executeTime=self.executeTime, curSwitchTime=self.curSwitchTime))
                self.curSwitchTime -= 1
                self.checkContextSwitchFinish()
            elif self.state == WORKING:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: Job# {jobId} executing in burst# {curBurstTime}: CPU time remain: {CPUTime}"
                #         .format(executeTime=self.executeTime, jobId=self.curJob.getId(), curBurstTime=self.curJob.getCurBurstTime(),
                #                 CPUTime=self.curJob.getCurCPUTime()))
                self.curJob.execute()
            # Time unit end
            self.chekcCurJobFinish()
            if self.isSimFinish():
                if self.isVerboseMode:
                    print("==================================================")
                print("{name}: Simulation Ended.".format(name=self.name))
                break
            self.executeTime += 1
            # if self.isVerboseMode:
            #     self.log("==================================================")
        print("{name}:".format(name=self.name))
        self.log("Shorest Job First:")
        self.log("Total Time required is {executeTime} time units"
              .format(executeTime=self.executeTime))
        self.log("CPU Utilization is {CPUUtilization}"
              .format(CPUUtilization=self.getCPUUtilization()))
        if self.isDetailedMode:
            for job in self.finishedJobList:
                self.log("")
                job.showFinishState(self.log)
        self.log("==================================================")

    # Shortest remain time next
    def srtn(self):
        print("{name}: Start Simulation...".format(name=self.name))
        print("==================================================")
        while True:
            # Time unit start
            if self.checkJobArrival():
                self.waitList.sort(key=operator.attrgetter('curMaxCPUTime'))
            self.checkAvaiableJob()
            # Time unit running
            if self.state == IDLE:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: CPU in idle."
                #           .format(executeTime=self.executeTime))
                self.idleTime += 1
            elif self.state == CONTEXT_SWITCH:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: Context switch occuring, remaining time: {curSwitchTime}"
                #           .format(executeTime=self.executeTime, curSwitchTime=self.curSwitchTime))
                self.curSwitchTime -= 1
                self.checkContextSwitchFinish()
            elif self.state == WORKING:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: Job# {jobId} executing in burst# {curBurstTime}: CPU time remain: {CPUTime}"
                #         .format(executeTime=self.executeTime, jobId=self.curJob.getId(), curBurstTime=self.curJob.getCurBurstTime(),
                #                 CPUTime=self.curJob.getCurCPUTime()))
                self.curJob.execute()
                if len(self.waitList) > 0:
                    if self.curJob.getCurCPUTime() > self.waitList[0].getCurCPUTime():
                        self.preemption()
            # Time unit end
            # Time unit end
            self.chekcCurJobFinish()
            if self.isSimFinish():
                if self.isVerboseMode:
                    print("==================================================")
                print("{name}: Simulation Ended.".format(name=self.name))
                break
            self.executeTime += 1
            # if self.isVerboseMode:
            #     self.log("==================================================")
        print("{name}:".format(name=self.name))
        self.log("Shorest Remaining Time Next:")
        self.log("Total Time required is {executeTime} time units"
              .format(executeTime=self.executeTime))
        self.log("CPU Utilization is {CPUUtilization}"
              .format(CPUUtilization=self.getCPUUtilization()))
        if self.isDetailedMode:
            for job in self.finishedJobList:
                self.log("")
                job.showFinishState(self.log)
        self.log("==================================================")

    # Round-Robin
    def rr(self):
        print("{name}: Start Simulation...".format(name=self.name))
        print("==================================================")
        while True:
            # Time unit start
            self.checkJobArrival()
            self.checkAvaiableJob()
            # Time unit running
            if self.state == IDLE:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: CPU in idle."
                #           .format(executeTime=self.executeTime))
                self.idleTime += 1
            elif self.state == CONTEXT_SWITCH:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: Context switch occuring, remaining time: {curSwitchTime}"
                #           .format(executeTime=self.executeTime, curSwitchTime=self.curSwitchTime))
                self.curSwitchTime -= 1
                self.checkContextSwitchFinish()
            elif self.state == WORKING:
                # if self.isVerboseMode:
                #     self.log("At time unit# {executeTime}: Job# {jobId} executing in burst# {curBurstTime}: CPU time remain: {CPUTime}"
                #         .format(executeTime=self.executeTime, jobId=self.curJob.getId(), curBurstTime=self.curJob.getCurBurstTime(),
                #                 CPUTime=self.curJob.getCurCPUTime()))
                self.curJob.execute()
                self.curQuantumTime -= 1
                if self.curQuantumTime <= 0:
                        self.preemption()
            # Time unit end
            self.chekcCurJobFinish()
            if self.isSimFinish():
                if self.isVerboseMode:
                    print("==================================================")
                print("{name}: Simulation Ended.".format(name=self.name))
                break
            self.executeTime += 1
            # if self.isVerboseMode:
            #     self.log("==================================================")
        print("{name}:".format(name=self.name))
        self.log("Round-Robin (Quantum {quantumTime}):".format(quantumTime=self.quantumTime))
        self.log("Total Time required is {executeTime} time units"
              .format(executeTime=self.executeTime))
        self.log("CPU Utilization is {CPUUtilization}"
              .format(CPUUtilization=self.getCPUUtilization()))
        if self.isDetailedMode:
            for job in self.finishedJobList:
                self.log("")
                job.showFinishState(self.log)
        self.log("==================================================")