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
        self.remainCPUTime = 0
        self.enterTime = 0
        self.totalIOTime = 0
        self.executeTime = 0
        self.finishTime = 0
    
    # Function to go to next burst when current burst done (Ususally called on running simulations)
    def goToNextBurst(self):
        self.curBurstTime += 1
        if self.curBurstTime < self.burstTime:
            self.remainCPUTime = self.burstList[self.curBurstTime][CPU_TIME]
        else:
            self.finish = True

    # Function to Add a new burst data (Usually called when creating new process)
    def addBurst(self, burstNum, CPUTime, IOTime):
        self.burstList.append([burstNum, CPUTime, IOTime])
        if len(self.burstList) == 1:
            self.remainCPUTime = CPUTime

    # Getter and Setter
    def setEnterTime(self, enterTime):
        self.enterTime = enterTime
    
    def minusCurCPUTime(self, deltaTime):
        self.remainCPUTime -= deltaTime

    def addTotalIOTime(self, deltaTime):
        self.totalIOTime += deltaTime

    def addExecuteTime(self, deltaTime):
        self.executeTime += deltaTime

    def setFinishTime(self, finishTime):
        self.finishTime = finishTime

    def getId(self):
        return self.id + 1
    
    def getArrivalTime(self):
        return self.arraivalTime

    def getBurstTime(self):
        return self.burstTime
    
    def getCurBurstTime(self):
        return self.curBurstTime

    def getRemainBurstTime(self):
        return self.burstTime - self.curBurstTime

    def getRemainCUPTime(self):
        return self.remainCPUTime
    
    def getIOTime(self):
        return self.burstList[self.curBurstTime][IO_TIME]

    def getEnterTime(self):
        return self.enterTime
    
    def isLastBurst(self):
        return self.curBurstTime == self.burstTime - 1
    
    def getTAT(self):
        return self.finishTime - self.arraivalTime
    
    # Function to show basic info of process (Called in detailed mode)
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