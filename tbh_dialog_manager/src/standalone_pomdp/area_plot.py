import numpy as np
from pylab import *
np.random.seed(153)

N = 5
x = np.arange(0,N)
y1 = np.random.rand(N)
y2 = y1 + np.random.rand(N)
y3 = np.array([1]*N)
plot(x,y1)
plot(x,y2)

fill_between(x,y1,0,color='cyan')
fill_between(x,y2,y1,color='magenta')
fill_between(x,y3,y2,color='red')
show()

x = np.arange(0,N,0.01)
y4 = np.sqrt(x)
plot(x,y4,color='k',lw=2)
fill_between(x,y4,0,color='0.8')
show()
