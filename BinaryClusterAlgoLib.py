'''
Module containing all functions related to simulating the Binary-Disk Model through a Monte-Carlo Pivot Algorithm.
Based on functions in lecture notes, see lectureFunctions.py
'''
import numpy as np
rng = np.random.default_rng()
import math as m
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import deque


#Functions:

def createState(N,n,r,L):
    '''Returns a state, representing a square with sides L, N circles with radius R=1, and n circles with radius r.
    States have form { "positions" : [(float,float)], "size": [float], "L": int, "occArray": [] }'''
    positions = np.zeros((N+n,2))
    size = np.zeros(N+n)
    R=1

    #Putting all big circles on a grid, starting at 0,0
    if (R==1):
        x,y = 0,0
        for i in range(N):
            if (L-x < 2*R):
                y+=2*R
                x=0
            else:
                x+= 2*R
            positions[i] = [x,y]
            size[i] = R
    else:
        return "ERROR: not implemented for R!=1"

    #Putting all small circles on a grid, starting from -R+r,-R+r, going down
    if (True):
        x,y = 0,L-R-r
        for i in range(n):
            if (L-x < 2*r):
                y-=2*r
                x=0
            else:
                x+= 2*r
            positions[N+i] = [x,y]
            size[N+i] = r
    
   #create occArray:
    occArray = np.ndarray((L,L), dtype=object)
    for i in range(L):
        for j in range(L):
            occArray[i,j] = []

    for i in range(N+n):
        x,y = positions[i]
        x,y = int(x)%L, int(y)%L
        occArray[x,y].append(i)
    return {"positions": positions, "size": size, "occArray": occArray, "L":L, "N":N, "n":n}

def createStateDensity(N,n,r,d):
    Acircles = m.pi*(N+(r**2)*n)
    L = m.ceil(m.sqrt(d/Acircles))  #round up?
    return createState(N,n,r,L)

def plotOneState(state, name="..."):
    '''Plot a state using matplotlib'''
    L = state["L"]
    fig, ax = plt.subplots()
    ax.set_ylim(0,state["L"])
    ax.set_xlim(0,state["L"])
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_yticks([])
    ax.set_xticks([])
    for i in range(len(state["size"])):
        (x,y) = state["positions"][i]
        r = state["size"][i]
        for x_shift in [z for z in x + [-L,0,L] if -r<z<L+r]:
            for y_shift in [z for z in y + [-L,0,L] if -r<z<L+r]:
                ax.add_patch(plt.Circle((x_shift,y_shift),r))
    if (name=="..."):
        name = "testplot.jpeg"
    plt.savefig(name)

def clearDisk(state,index):
    occX, occY = state["positions"][index]
    occX, occY = int(occX)%state["L"], int(occY)%state["L"]
    #print(index)
    #print(state["positions"])
    #print(state["occArray"])
    #print([occX,occY])
    indexInOcc = state["occArray"][occX,occY].index(index)
    state["occArray"][occX,occY].pop(indexInOcc)

def addDisk(state,index):
    occX, occY = state["positions"][index]
    occX, occY = int(occX)%state["L"],int(occY)%state["L"]
    state["occArray"][occX,occY].append(index)

def pointReflect(point, pivot, L):
    point[:] = (2*pivot - point)%L

def getOverlap(state, index):
    R = state["size"][index]
    L = state["L"]
    x,y = state["positions"][index]
    xSquare,ySquare = int(x), int(y)
    overlap = []

    #big circles: check in 5x5 centred on circle
    if (True):
        for dX in range(-3,3): #wht 3?
            thisXSquare = (xSquare+dX) % L
            for dY in range(-3,3):
                thisYSquare = (ySquare+dY) % L
                circlesToCheck = state["occArray"][thisXSquare,thisYSquare]
                for circle in circlesToCheck:
                    distance = findDistance(state,index,circle)
                    thisR = state["size"][circle]
                    if ( distance < R+thisR):
                        #check if fully covered (small circle represented by square for convenience):
                        if (distance+thisR < R):
                            overlap.append((circle,True))
                        else:
                            overlap.append((circle,False))
    return overlap



def randomDiskClusterMove(state):
    '''Move a random (large or small) disk and update the state accordingly.'''
    index = rng.integers(0,len(state["size"]))
    pivot = rng.uniform(0,state["L"],2)
    diskClusterMove(state,index,pivot)



def diskClusterMove(state,index,pivot):
    toMove = deque()
    moved = []
    toMove.appendleft(index)
    clearDisk(state,index)
    moved.append(index)
    while toMove:
        thisDisk = toMove.pop()
        pointReflect(state["positions"][thisDisk], pivot, state["L"])
        overlap = getOverlap(state,thisDisk)
        for (diskToMove, isCovered) in overlap:
            clearDisk(state,diskToMove)
            moved.append(diskToMove)
            if isCovered:
                pointReflect(state["positions"][diskToMove], pivot, state["L"])
            else:
                toMove.appendleft(diskToMove)
            
    #Original added disks immidiatly, but this caused some problem. This fixes it, but the original problem suggests our code is still wrong somewhere...
    for i in range(len(moved)):
        addDisk(state,moved[i])

def findDistance(state,i,j):
    x1,y1 = state["positions"][i]
    x2,y2 = state["positions"][j]
    dx, dy = abs(x1-x2), abs(y1-y2)
    dx, dy = min(dx, state["L"]-dx), min(dy, state["L"]-dy)
    return (m.sqrt(dx**2 + dy**2))

def findDavg(state):
    cumDistance = 0
    for i in range(state["N"]):
        for j in range(i+1, state["N"]):
            cumDistance += findDistance(state,i,j)
    return cumDistance / (state["N"]*(state["N"]-1)/2)






