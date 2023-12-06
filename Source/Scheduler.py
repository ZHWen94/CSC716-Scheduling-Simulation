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
        # Bool to control simulation run state
        self.isRun = True
        # Log File to record output
        self.logFile = logFile
        # Timer for scheduler
        self.idleTime = 0
        self.executeTime = 0
        # Context switch timer and bool
        self.switchTime = 0
        self.curSwitchTime = 0
        self.state = IDLE
        # Ready and finish qeuen
        self.jobList = []
        self.waitQeuen = []
        self.readyQeuen = []
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
        # Algorithm Name Dict
        self.algorithmName = {
            "fcfs": "First Come First Serve",
            "sjf": "Shortest Job First",
            "srtn": "Shortest Remaining Time Next",
            "rr": "Roundrobin(Quantum: {quantumTime})".format(quantumTime=self.quantumTime),
        }
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
                        for job in self.jobList:
                            self.log("")
                            job.toString(self.log)
                        self.log("==================================================")
                    if self.isVerboseMode:
                        self.log(self.algorithmName[self.selectedAlgorithm])
                    self.simulation()
                elif confirm == "n":
                    isConfirmed = True
                    print("{name}: Simulation Aborted.".format(name=self.name))
        else:
            print("Unknown Error: Empty JobList, Simulation Aborted.")

    # Simulation Function
    def simulation(self):
        print("{name}: Start Simulation...".format(name=self.name))
        if self.isVerboseMode:
            print("==================================================")
        while self.isRun:
            # Time unit start
            if self.checkJobArrival():
                if self.selectedAlgorithm == "sjf":
                    self.readyQeuen.sort(key=operator.attrgetter('curMaxCPUTime'))
                elif self.selectedAlgorithm == "srtn":
                    self.readyQeuen.sort(key=operator.attrgetter('curMaxCPUTime'))
                    try:
                        if self.curJob.getCurCPUTime() > self.readyQeuen[0].getCurCPUTime():
                            self.preemption()
                    except AttributeError:
                        pass
            self.checkAvaiableJob()
            # Time unit in-running
            self.timeForward()
            # Time unit end
            self.doIO()
            self.executeTime += 1
            if self.state == WORKING:
                self.chekcCurJobFinish()
            elif self.state == CONTEXT_SWITCH:
                self.checkContextSwitchFinish()
            self.checkSimFinish()
            # if self.isVerboseMode:
            #     self.log("==================================================")
        print("{name}:".format(name=self.name))
        self.log("{algorithmName}".format(algorithmName=self.algorithmName[self.selectedAlgorithm]))
        self.log("Total Time required is {executeTime} time units"
              .format(executeTime=self.executeTime))
        self.log("CPU Utilization is {CPUUtilization: .2%}"
              .format(CPUUtilization=self.getCPUUtilization()))
        if self.isDetailedMode:
            for job in self.finishedJobList:
                self.log("")
                job.showFinishState(self.log)
        self.log("==================================================")

    # Function to do IO for jobs in wait qeuen
    def doIO(self):
        for job in self.waitQeuen:
            job.io()
            if job.getCurIOTime() <= 0:
                job.goToNextBurst()
                if self.isVerboseMode:
                    self.log("At time unit {executeTime}: Job# {jobId} finish IO, and moving from wait to ready qeuen."
                        .format(executeTime=self.executeTime, jobId=job.getId()))
                self.readyQeuen.append(job)
                self.waitQeuen.remove(job)

    # Function to check a new job arrive and put into wait list
    def checkJobArrival(self):
        isNewJobArrived = False
        while len(self.jobList) > 0:
            if self.jobList[0].getArrivalTime() == self.executeTime:
                if self.isVerboseMode:
                    self.log("At time unit# {executeTime}: Job# {jobId} arrived, and moving in the ready qeuen."
                        .format(executeTime=self.executeTime, jobId=self.jobList[0].getId()))
                self.readyQeuen.append(self.jobList.pop(0))
                isNewJobArrived = True
            if len(self.jobList) <= 0:
                return isNewJobArrived
            elif self.jobList[0].getArrivalTime() != self.executeTime:
                return isNewJobArrived

    # Function to check if cpu is idle and job is in wait list
    def checkAvaiableJob(self):
        if self.state == IDLE and len(self.readyQeuen) > 0:
            if self.isVerboseMode:
                self.log("At time unit {executeTime}: Job# {jobId} moving from readay qeuen to execute."
                      .format(executeTime=self.executeTime, jobId=self.readyQeuen[0].getId()))
            self.curJob = self.readyQeuen.pop(0)
            self.state = WORKING

    # Function run the current time unit
    def timeForward(self):
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
        elif self.state == WORKING:
            # if self.isVerboseMode:
            #     self.log("At time unit# {executeTime}: Job# {jobId} executing in burst# {curBurstTime}: CPU time remain: {CPUTime}"
            #         .format(executeTime=self.executeTime, jobId=self.curJob.getId(), curBurstTime=self.curJob.getCurBurstTime(),
            #                 CPUTime=self.curJob.getCurCPUTime()))
            self.curJob.execute()
            if self.selectedAlgorithm == "rr":
                self.curQuantumTime -= 1
                if self.curQuantumTime <= 0:
                    self.preemption()

    # Function to check a current job is done
    def chekcCurJobFinish(self):
        if self.state == WORKING and self.curJob.isCurBurstFinish():
            if not self.curJob.isLastBurst():
                if self.isVerboseMode:
                    self.log("At time unit# {executeTime}: Job# {jobId} finish Burst# {burstNum}"
                        .format(executeTime=self.executeTime, jobId=self.curJob.getId(), burstNum=self.curJob.getCurBurstTime()))
                self.waitQeuen.append(self.curJob)
                self.curJob = None
                self.contextSwitch()
            else:
                if self.isVerboseMode:
                    self.log("At time unit# {executeTime}: Job# {jobId} finish."
                        .format(executeTime=self.executeTime, jobId=self.curJob.getId()))
                self.finishedJobList.append(self.curJob)
                self.curJob.setFinishTime(self.executeTime)
                self.curJob = None
                self.contextSwitch()

    # Function to check simulation finish
    def checkSimFinish(self):
        if self.state == IDLE and len(self.readyQeuen) == 0 and len(self.jobList) == 0:
            self.log("==================================================")
            print("{name}: Simulation Ended.".format(name=self.name))
            self.isRun = False

    # Action Function
    # Function to start a preemtion
    def preemption(self):
        if self.isVerboseMode:
            self.log("At time unit# {executeTime}: Preemption occured, Job# {jobId} move to wait."
                  .format(executeTime=self.executeTime, jobId=self.curJob.getId()))
        self.readyQeuen.append(self.curJob)
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
    
    # Function to check context switch finish
    def checkContextSwitchFinish(self):
        if self.curSwitchTime <= 0:
            if self.isDetailedMode:
                self.log("At time unit# {executeTime}: Context switch finish."
                        .format(executeTime=self.executeTime))
            self.state = IDLE
            self.curQuantumTime = self.quantumTime

    # Function to calculate cpu utilization
    def getCPUUtilization(self):
        return (self.executeTime - self.idleTime) / self.executeTime