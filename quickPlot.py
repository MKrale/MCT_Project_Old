import matplotlib.pyplot as plt

ds = [0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75]
Davgs = [17.7,13.2,10.97,9.44,8.59,7.79,7.04,6.73,6.28,6.33,5.93,5.53,5.53,5.12,5.11]

plt.plot(ds,Davgs)
plt.savefig("dirtyPlot.png")