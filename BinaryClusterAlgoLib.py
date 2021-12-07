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
    if L/100 < 2*r:
        nmbrCells = m.ceil(L/r)
        print("nmbrCells changed to "+str(nmbrCells))
    else:
        nmbrCells = 100 
    cellSize = L/nmbrCells

    #Putting all big circles on a grid, starting at 0,0
    if (R==1):
        x,y = -R,R
        for i in range(N):
            if (L-x < 3*R):
                y+=2*R
                x=R
            else:
                x+= 2*R
            positions[i] = [x,y]
            size[i] = R
    else:
        return "ERROR: not implemented for R!=1"

    #Putting all small circles on a grid, starting from -R+r,-R+r, going down
    if (True):
        x,y = -r,L-r
        for i in range(n):
            if (L-x < 2*r):
                y-=2*r
                x=0
            else:
                x+= 2*r
            positions[N+i] = [x,y]
            size[N+i] = r
    
    #create occArray:
    #occArray = np.ndarray((L,L), dtype=object)
    occArray = np.ndarray((nmbrCells,nmbrCells), dtype=object)
    for i in range(nmbrCells):
        for j in range(nmbrCells):
            occArray[i,j] = []

    for i in range(N+n):
        x,y = positions[i]
        x,y = int(x*nmbrCells/L)%nmbrCells, int(y*nmbrCells/L)%nmbrCells
        occArray[x,y].append(i)

    return {"positions": positions, "size": size, "occArray": occArray, "L":L, "N":N, "n":n, "R":R,"r":r, "cellSize":cellSize, "nmbrCells":nmbrCells}

def findCellCoords(state, index):
    x,y = state["positions"][index]
    L = state["L"]
    return int(x*state["nmbrCells"]/L)%state["nmbrCells"], int(y*state["nmbrCells"]/L)%state["nmbrCells"]

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
    occX, occY = findCellCoords(state,index)
    indexInOcc = state["occArray"][occX,occY].index(index)
    state["occArray"][occX,occY].pop(indexInOcc)

def addDisk(state,index):
    occX, occY = findCellCoords(state,index)
    state["occArray"][occX,occY].append(index)

def pointReflect(point, pivot, L):
    point[:] = (2*pivot - point)%L

def canCollide(state,index):
    occX,occY = findCellCoords(state,index)
    if index in state["occArray"][occX,occY]:
        return True
    return False

def getOverlapCircles(state,i,j):
    distance = findDistance(state,i,j)
    Ri,Rj = state["size"][i],state["size"][j]
    if ( distance < Ri+Rj):
        #check if fully covered (small circle represented by square for convenience):
        if (distance+Rj < Ri):
            return[(j,True)]
        else:
            return[(j,False)]
    return []

def getOverlap(state, index):
    R = state["size"][index]
    L = state["L"]
    x,y = state["positions"][index]
    xSquare,ySquare = findCellCoords(state,index)
    overlap = []

    #check which cells need to be checked
    if (2*R < state["cellSize"]):
        cellsToCheck = 1
    elif(R ==1):
        cellsToCheck = m.ceil(R/state["cellSize"])+m.ceil(state["r"]/state["cellSize"])+1
    else:
        cellsToCheck = m.ceil(R/state["cellSize"])*4+1

    #check neighbouring cells for overlap with small circles
    circlesToCheck = [] #For some reason we are getting duplicates here, how could that be?
    for dX in range(-cellsToCheck,cellsToCheck): 
        thisXSquare = (xSquare+dX) % state["nmbrCells"]
        for dY in range(-cellsToCheck,cellsToCheck):
            thisYSquare = (ySquare+dY) % state["nmbrCells"]
            circlesToCheck.extend(set((state["occArray"][thisXSquare,thisYSquare])))

    for circle in circlesToCheck:
        if circle>=state["N"]:
            overlap.extend(getOverlapCircles(state,index,circle))

    #check with all big circles, required for smaller circles:
    for i in range(state["N"]):
        if canCollide(state,i):
            overlap.extend(getOverlapCircles(state,index,i))
    return overlap



def randomDiskClusterMove(state):
    '''Move a random (large or small) disk and update the state accordingly.'''
    index = rng.integers(0,len(state["size"]))
    pivot = rng.uniform(0,state["L"],2)
    diskClusterMove(state,index,pivot)

def bigDiskClusterMove(state):
    '''Move a random large disk and update the state accordingly.'''
    index = rng.integers(0,state["N"])
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






