# CSC716 PROJECT TOPIC#1: CPU SCHEDULING ALGORITHMS COMPARISON
# Team: Zehui Wen, Meng Meng, Dylan Contractor

# Process Module
# This is a class file for the process class
# Use this class to create a process object to represent an process in simulation

# Constant variables
BURST_NUMBER = 0
CPU_TIME = 1
IO_TIME = 2

class Processes(object):
    # Consturctor
    def __init__(self, id, arrivalTime, burstTime):
        self.id = id
        self.arraivalTime = arrivalTime
        self.burstTime = burstTime
        self.curBurstTime = 0
        self.burstList = []
        self.curMaxCPUTime = 0
        self.curCPUTime = 0
        self.curMaxIOTime = 0
        self.curIOTime = 0
        self.totalIOTime = 0
        self.executeTime = 0
        self.finishTime = 0

    # Execute functions (Ususally called on running simulations)
    # Function to execute process with specify quantum time
    def execute(self):
        if self.curCPUTime > 0:
            self.executeTime += 1
            self.curCPUTime -= 1

    def io(self):
        if self.curIOTime > 0:
            self.curIOTime -= 1
            self.totalIOTime += 1
    
    # Function to go to next burst when current burst done (Ususally called on running simulations)
    def goToNextBurst(self):
        self.curBurstTime += 1
        if self.curBurstTime < self.burstTime:
            self.curMaxCPUTime = self.burstList[self.curBurstTime][CPU_TIME]
            self.curCPUTime = self.curMaxCPUTime
            if self.curBurstTime < self.burstTime - 1:
                self.curMaxIOTime = self.burstList[self.curBurstTime][IO_TIME]
                self.curIOTime = self.curMaxIOTime
        else:
            self.finish = True        

    # Function to Add a new burst data (Usually called when creating new process)
    def addBurst(self, burstNum, CPUTime, IOTime):
        self.burstList.append([burstNum, CPUTime, IOTime])
        if len(self.burstList) == 1:
            self.curMaxCPUTime = CPUTime
            self.curCPUTime = CPUTime
            self.curMaxCPUTime = IOTime
            self.curIOTime = IOTime

    # Getter and Setter
    def setFinishTime(self, finishTime):
        self.finishTime = finishTime

    def getId(self):
        return self.id + 1
    
    def getArrivalTime(self):
        return self.arraivalTime

    def getBurstTime(self):
        return self.burstTime
    
    def getCurBurstTime(self):
        return self.curBurstTime + 1

    def getRemainBurstTime(self):
        return self.burstTime - self.curBurstTime
    
    def getBurstList(self):
        return self.burstList
    
    def getNextCPUTime(self):
        return self.burstList[self.curBurstTime][CPU_TIME]

    def getCurCPUTime(self):
        return self.curCPUTime
    
    def getCurIOTime(self):
        return self.curIOTime

    def isCurBurstFinish(self):
        return self.curCPUTime <= 0
    
    def isLastBurst(self):
        return self.curBurstTime == self.burstTime - 1

    def isFinish(self):
        return self.curBurstTime >= self.burstTime
    
    def getTAT(self):
        return self.finishTime - self.arraivalTime
    
    # Function to show basic info of process
    def toString(self, logFunct):
        logFunct("Process# {id}:".format(id=self.id+1))
        logFunct("Arrival Time: {arrivalTime}, Burst Time: {burstTime}"
              .format(arrivalTime=self.arraivalTime, burstTime=self.burstTime))
        for burst in self.burstList:
            curIOTime = burst[IO_TIME]
            if curIOTime != 0:
                logFunct("Burst# {burstNum}: CPU({CPUTime}), IO({IOTime})"
                    .format(burstNum=burst[BURST_NUMBER]+1, CPUTime=burst[CPU_TIME], IOTime=curIOTime))
            else:
                logFunct("Burst# {burstNum}: CPU({CPUTime})"
                    .format(burstNum=burst[BURST_NUMBER]+1, CPUTime=burst[CPU_TIME]))
    
    # Function to show finish info of process when it done (Called in detailed mode)
    def showFinishState(self, logFunct):
        logFunct("Process# {id}:".format(id=self.id+1))
        logFunct("Arrival Time: {arrivalTime}"
                .format(arrivalTime=self.arraivalTime))
        logFunct("Service Time: {executeTime}"
                .format(executeTime=self.executeTime))
        logFunct("I/O Time: {totalIOTime}"
                .format(totalIOTime=self.totalIOTime))
        logFunct("Finish Time: {finishTime}"
                .format(finishTime=self.finishTime))
        logFunct("TAT: {TAT}".format(TAT=self.getTAT()))