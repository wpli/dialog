import numpy as np

def lognormalize(x):
    a = np.logaddexp.reduce(x)
    return np.exp(x - a)

if __name__ == '__main__':
    x = np.array( [ -3, -2, -7 ] )
    print x
    y = lognormalize(x)
    print y
    
