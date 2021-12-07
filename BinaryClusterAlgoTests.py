'''
Code used to manually write tests for binary clusters, as well as to test our Binary Cluster Algorithm library.
'''
import BinaryClusterAlgoLib as bca
import numpy as np
import time

# Space for code to run for testing: should be removed before using the module!
def bigTest():
    
    s = bca.createState(20,7000,0.05, 12)
    startTime = time.perf_counter()
    for i in range(1000):
            bca.randomDiskClusterMove(s)
            #bca.bigDiskClusterMove(s)
    spentTime = time.perf_counter() - startTime
    print("Time for 100 moves: "+str(spentTime))
    bca.plotOneState(s)
    # Random moves with example-settings: 0.08s (L=12)
    # Big-circle moves with example-settings: 0.12s (L=12) -> still big circles don't change much...

def timeTest():
    # As used in the book:
    d = 0.36       # >0.01 s/move, Davg = 7.04, sdt = 0.07
    #d = 0.52       # 0.01 s/move, Davg = 5.90, std = 0.05
    #d = 0.7        # 0.035 s/move, Davg = 4.89, std = 0.13

    # As found by trial and error:
    N = 1000 # moves between measurements
    NI = 1000 # initialisation moves
    M = 10 # nmbr of measurements

    startTime = time.perf_counter()
    s = bca.createStateDensity(18,7200,0.05,d)
    thisName = "../Results/bookTest_startState_d="+str(d)+"_N="+str(N)+".png"
    bca.plotOneState(s,thisName)
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
        thisName = "../Results/bookTest_d="+str(d)+"_N="+str(N)+"_M="+str(i)+".png"
        bca.plotOneState(s,thisName)

    spentTime = time.perf_counter() - startTime - initTime
    print("Measurement Complete! ("+str(N)+" Cluster moves takes per measurement, "+str(M)+" measurements, in "+str(spentTime)+"s).")
    Davg = np.mean(Davgs)
    Dstd = np.std(Davgs)
    print("Mean Distance: "+str(Davg)+", with std "+str(Dstd)+"." )
    bca.plotOneState(s)

def dDependencyTest():
    M = 10
    N = 1000
    NI = 2*N
    densities = np.arange(0.05,0.751,0.05)

    f=open("D_DependencyTest_N="+str(N)+"_M="+str(M)+".txt", 'x')
    f.write("Testing D_Dependency with following settings:\nN = "+str(N)+"\nM = "+str(M)+"\nds = "+str(densities)+"\n\n\n")
    startTime = time.perf_counter()

    for d in densities:
        Davgs = []
        print("Setting up for d="+str(d)+":")
        f.write("d = "+str(d)+":\nDavg = [")
        s = bca.createStateDensity(18,7200,0.05,d)
        for i in range(NI):
            bca.randomDiskClusterMove(s)
        print("Setup complete!")
        for i in range(M):
            for j in range(N):
                bca.randomDiskClusterMove(s)
            Davgs.append(bca.findDavg(s))
            print("after "+str(N*(i+1))+" Moves, Davg="+str(Davgs[i])+".")
            if i!=0:
                f.write(",")
            f.write(str(Davgs[i]))
            
        Davg = np.mean(Davgs)
        Dstd = np.std(Davgs)
        print("\n\nRESULT: for d = "+str(d)+", mean Distance: "+str(Davg)+", with std "+str(Dstd)+".\n\n" )
        f.write("]\nMean Davg = "+str(Davg)+"\ndeviation = "+str(Dstd)+ "\n\n")
    f.close()

    endTime = time.perf_counter()-startTime
    print("Total run took "+str(endTime)+"s.")
dDependencyTest()