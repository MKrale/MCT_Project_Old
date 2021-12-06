'''
Module containing all functions related to simulating the Binary-Disk Model through a Monte-Carlo Pivot Algorithm.
Copied from lecture notes of course Monte Carlo Techniques.
'''

def plot_disk_configuration(positions,L,ax,color):
    '''Plot disk configuration. color is an array of bools specifying blue or green color.'''
    ax.set_aspect('equal')
    ax.set_ylim(0,L)
    ax.set_xlim(0,L)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_yticks([])
    ax.set_xticks([])
    for i, x in enumerate(positions):
        # consider all horizontal and vertical copies that may be visible
        for x_shift in [z for z in x[0] + [-L,0,L] if -1<z<L+1]:
            for y_shift in [z for z in x[1] + [-L,0,L] if -1<z<L+1]:
                col = '#2222ff' if color[i] else '#22cc77'
                ax.add_patch(plt.Circle((x_shift,y_shift),1,color=col))

def occupation_array(l,pos):
    '''Return l*l array with indices of positions of disks in regular grid, -1 when empty.'''
    occupation = -np.ones((l,l),dtype='int')
    for i, (x, y) in enumerate(pos):
        occupation[int(x),int(y)] = i
    return occupation

def get_overlap(state,point):
    '''Return a list of indices of disks that have overlap with point.'''
    w = len(state["occ"])
    overlaps = []
    for dx in range(-2,3):
        x = (int(point[0]) + dx)%w
        for dy in range(-2,3):
            y = (int(point[1]) + dy)%w
            index = state["occ"][x,y]
            if index >= 0 and ( ((point[0]%1)-(state["x"][index,0]%1)-dx)**2 +
                                ((point[1]%1)-(state["x"][index,1]%1)-dy)**2 < 4):
                overlaps.append(index)
    return overlaps

def clear_disk(state,index):
    '''Remove disk from occupation array.'''
    state["occ"][int(state["x"][index,0]),int(state["x"][index,1])] = -1
def add_disk(state,index):
    '''Add disk to occupation array.'''
    state["occ"][int(state["x"][index,0]),int(state["x"][index,1])] = index

def point_reflect(pt,pivot,l):
    '''Reflect the point pt in the pivot (with periodic boundary conditions of length l).'''
    pt[:] = (2*pivot - pt)%l

def disk_cluster_move(state,index,pivot):
    '''Iteratively reflect disks in pivot, starting with index, until no more overlaps occur.'''
    movers = deque()
    movers.appendleft(index)
    clear_disk(state,index)
    while movers:
        mover = movers.pop()
        point_reflect(state["x"][mover],pivot,len(state["occ"]))
        overlap = get_overlap(state,state["x"][mover])
        for i in overlap:
            movers.appendleft(i)
            clear_disk(state,i)
        add_disk(state,mover)

def random_disk_cluster_move(state):
    '''Perform cluster move starting with random initial disk and uniform random pivot.'''
    index = rng.integers(0,len(state["x"]))
    pivot = rng.uniform(0,len(state["occ"]),2)
    disk_cluster_move(state,index,pivot)