'''
Module containing all functions related to simulating the Binary-Disk Model through a Monte-Carlo Pivot Algorithm.
Based on functions in lecture notes, see lectureFunctions.py
'''
import numpy as np
rng = np.random.default_rng()
import math as m
import matplotlib
matplotlib.use('Agg') #required for my machine: can probably be removed on others
import matplotlib.pyplot as plt
from collections import deque


#   Helper functions:

def findCellCoords(state, index):
    '''Returns cell coordinates of given circle.'''
    x,y = state["positions"][index]
    L = state["L"]
    return int(x*state["nmbrCells"]/L)%state["nmbrCells"], int(y*state["nmbrCells"]/L)%state["nmbrCells"]

def clearDisk(state,index):
    '''Removes disk from Occupation Array.'''
    occX, occY = findCellCoords(state,index)
    indexInOcc = state["occArray"][occX,occY].index(index)
    state["occArray"][occX,occY].pop(indexInOcc)

def addDisk(state,index):
    '''Adds disk to Occupation Array.'''
    occX, occY = findCellCoords(state,index)
    state["occArray"][occX,occY].append(index)

def pointReflect(point, pivot, L):
    '''Changes position of circle index to one corresponding to a point-reflext in pivot.'''
    point[:] = (2*pivot - point)%L

def canCollide(state,index):
    '''Returns True if circle index is saved in Occupation Array in the right place, False otherwise.'''
    occX,occY = findCellCoords(state,index)
    if index in state["occArray"][occX,occY]:
        return True
    return False


#   Functions for finding overlapping circles:

def getOverlapCircles(state,i,j):
    '''Returns [(j,True)] if circle i fully covers circle j, [(j,False)] if circle i partially covers j, [] otherwise.'''
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
    '''Returns all circles that overlap with circle index that are also currently stored in Occupation Array.'''
    R = state["size"][index]
    L = state["L"]
    x,y = state["positions"][index]
    xSquare,ySquare = findCellCoords(state,index)
    overlap = []

    #Use current radius to find how many cells need to be checked for collision with small circles
    if (2*R < state["cellSize"]):
        cellsToCheck = 1
    elif(R ==1):
        cellsToCheck = m.ceil(R/state["cellSize"])+m.ceil(state["r"]/state["cellSize"])+1
    else:
        cellsToCheck = m.ceil(R/state["cellSize"])*4+1 # this can probably be smaller, but this seems to work at least...

    #check neighbouring cells for overlap with small circles
    circlesToCheck = [] 
    for dX in range(-cellsToCheck,cellsToCheck): 
        thisXSquare = (xSquare+dX) % state["nmbrCells"]
        for dY in range(-cellsToCheck,cellsToCheck):
            thisYSquare = (ySquare+dY) % state["nmbrCells"]
            circlesToCheck.extend((state["occArray"][thisXSquare,thisYSquare]))

    for circle in circlesToCheck:
        if circle>=state["N"]: #ignore big circles: these come later
            overlap.extend(getOverlapCircles(state,index,circle))

    #check collisions with big circles:
    for i in range(state["N"]):
        if canCollide(state,i):
            overlap.extend(getOverlapCircles(state,index,i))

    return overlap

#   Creating States:

def createStateDensity(N,n,r,d):
    '''Calls createState, but calculates L according to a the required density of all circles d.'''
    Acircles = m.pi*(N+(r**2)*n)
    L = m.ceil(m.sqrt(Acircles/d))  #rounding up: should we just round to nearest?
    return createState(N,n,r,L)

def createState(N,n,r,L):
    '''Returns a state, representing a square with sides L, N circles with radius R=1, and n circles with radius r.
    States have form { "positions" : [(float,float)], "size": [float], "L": int, "occArray": [] }'''
    positions = np.zeros((N+n,2))
    size = np.zeros(N+n)
    R=1

    #Decide cell-size: L/100 default, but r if this is bigger (this makes calculations more efficient, we hope...)
    if L/100 < 2*r:
        nmbrCells = m.ceil(L/r)
        print("nmbrCells changed to "+str(nmbrCells))
    else:
        nmbrCells = 100 
    cellSize = L/nmbrCells

    #Putting all big circles on a grid, starting at R,R
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

    #Putting all small circles on a grid, starting from r,L-r, going down
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
    occArray = np.ndarray((nmbrCells,nmbrCells), dtype=object)
    for i in range(nmbrCells):
        for j in range(nmbrCells):
            occArray[i,j] = []

    for i in range(N+n):
        x,y = positions[i]
        x,y = int(x*nmbrCells/L)%nmbrCells, int(y*nmbrCells/L)%nmbrCells
        occArray[x,y].append(i)

    return {"positions": positions, "size": size, "occArray": occArray, "L":L, "N":N, "n":n, "R":R,"r":r, "cellSize":cellSize, "nmbrCells":nmbrCells}

#   Algorithm:

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
    '''Move a given (large or small) disk and update the state accordingly.'''
    #Initialise:
    toMove = deque()
    moved = []
    toMove.appendleft(index)
    clearDisk(state,index)
    moved.append(index)
    while toMove:
        #Take disk from toMove, point-reflect and find overlap
        thisDisk = toMove.pop()
        pointReflect(state["positions"][thisDisk], pivot, state["L"])
        overlap = getOverlap(state,thisDisk)
        #Remove all overlapping disks from occArray. Then, all disks that were completly covered can be point-reflected immidiatly, all others are added to toMove.
        for (diskToMove, isCovered) in overlap:
            clearDisk(state,diskToMove)
            moved.append(diskToMove)
            if isCovered:
                pointReflect(state["positions"][diskToMove], pivot, state["L"])
            else:
                toMove.appendleft(diskToMove)
            
    #Add removed disks back to Occupation Array
    for i in range(len(moved)):
        addDisk(state,moved[i])

#   Collecting Data:

def findDistance(state,i,j):
    '''Returns the distance between i and j.'''
    x1,y1 = state["positions"][i]
    x2,y2 = state["positions"][j]
    dx, dy = abs(x1-x2), abs(y1-y2)
    dx, dy = min(dx, state["L"]-dx), min(dy, state["L"]-dy)
    return (m.sqrt(dx**2 + dy**2))

def findDavg(state):
    '''Returns the average distance between all N large circles'''
    cumDistance = 0
    for i in range(state["N"]):
        for j in range(i+1, state["N"]):
            cumDistance += findDistance(state,i,j)
    return cumDistance / (state["N"]*(state["N"]-1)/2)

#   Plotting States:

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




