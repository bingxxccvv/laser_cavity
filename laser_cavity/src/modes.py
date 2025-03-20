import numpy as np
from scipy.special import hermite
from .gaussian_beam import CavityModeCalculator

def hermite_gaussian_mode(x, y, w, n=0, m=0):
    """计算厄米特-高斯模式"""
    X = np.sqrt(2) * x / w
    Y = np.sqrt(2) * y / w
    
    Hn = hermite(n)
    Hm = hermite(m)
    
    mode = (Hn(X) * Hm(Y) * 
            np.exp(-(X**2 + Y**2)/2) /
            np.sqrt(2**(n+m) * np.math.factorial(n) * np.math.factorial(m)))
    
    return mode

def calculate_higher_order_modes(cavity_params, fox_li, n_max=2, m_max=2):
    """计算高阶模式"""
    calc = CavityModeCalculator(cavity_params)
    gaussian_params = calc.calculate_eigenmode()
    
    modes = {}
    for n in range(n_max):
        for m in range(m_max):
            mode = hermite_gaussian_mode(fox_li.X, fox_li.Y, 
                                      gaussian_params.w0, n, m)
            modes[(n,m)] = mode
    
    return modes, gaussian_params