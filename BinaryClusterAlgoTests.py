'''
Code used to manually write tests for binary clusters, as well as to test our Binary Cluster Algorithm library.
'''
import BinaryClusterAlgoLib as bca
import numpy as np
import time

# Space for code to run for testing: should be removed before using the module!

startTime = time.perf_counter()
s = bca.createState(20,7000,0.1, 20)
for i in range(50):
        bca.randomDiskClusterMove(s)
spentTime = time.perf_counter() - startTime
print("Time: "+str(spentTime))
bca.plotOneState(s)
#s = bca.createStateDensity(20,7000,0.1,0.26)
#bca.plotOneState(s)

def timeTest():
    N = 500 # moves between measurements
    NI = 500 # initialisation moves
    M = 10 # nmbr of measurements

    startTime = time.perf_counter()
    for i in range(NI):
        bca.randomDiskClusterMove(s)
    initTime = time.perf_counter() - startTime
    print("Initialising complete! (t="+str(initTime)+").")

    Davgs = np.ndarray(M)
    for i in range(M):
        for j in range(N):
            bca.randomDiskClusterMove(s)
        Davgs[i] = bca.findDavg(s)
        print("Measurment "+str(i)+" complete! (Davg="+str(Davgs[i])+").")
        thisName = "../Results/testPlot_M="+str(i)+"_N="+str(N)+".png"
        bca.plotOneState(s,thisName)

    spentTime = time.perf_counter() - startTime - initTime
    print("Measurement Complete! ("+str(N)+" Cluster moves takes per measurement, "+str(M)+" measurements, in "+str(spentTime)+"s).")
    Davg = np.mean(Davgs)
    Dstd = np.std(Davgs)
    print("Mean Distance: "+str(Davg)+", with std "+str(Dstd)+"." )
    bca.plotOneState(s)
