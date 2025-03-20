import numpy as np
from scipy.fft import fft2, ifft2, fftshift, ifftshift
from typing import Tuple

class FoxLiCalculator:
    def __init__(self, wavelength: float, L: float, size: float, N: int = 512):
        self.wavelength = wavelength
        self.L = L
        self.size = size
        self.N = N
        self.dx = size / N
        self.k = 2 * np.pi / wavelength
        
        self.x = np.linspace(-size/2, size/2, N)
        self.y = self.x
        self.X, self.Y = np.meshgrid(self.x, self.y)
        
    def propagate_field(self, E: np.ndarray, z: float) -> np.ndarray:
        """使用角谱法传播场"""
        kx = 2 * np.pi * np.fft.fftfreq(self.N, self.dx)
        ky = kx
        KX, KY = np.meshgrid(kx, ky)
        
        H = np.exp(1j * z * np.sqrt(self.k**2 - KX**2 - KY**2))
        H = np.where(KX**2 + KY**2 <= self.k**2, H, 0)
        
        E_fft = fft2(E)
        E_prop = ifft2(E_fft * H)
        
        return E_prop
    
    def iterate(self, initial_field: np.ndarray, 
               R1: float, R2: float,
               max_iter: int = 100,
               tolerance: float = 1e-6) -> Tuple[np.ndarray, float]:
        """执行Fox-Li迭代"""
        E = initial_field.copy()
        
        def mirror_phase(R, x, y):
            if R == 0:  # 平面镜
                return 1
            return np.exp(-1j * self.k * (x**2 + y**2) / (2 * R))
        
        prev_loss = 0
        for i in range(max_iter):
            E = self.propagate_field(E, self.L)
            E *= mirror_phase(R2, self.X, self.Y)
            E = self.propagate_field(E, self.L)
            E *= mirror_phase(R1, self.X, self.Y)
            
            power = np.sum(np.abs(E)**2)
            loss = 1 - power
            E = E / np.sqrt(power)
            
            if abs(loss - prev_loss) < tolerance:
                break
            prev_loss = loss
            
        return E, loss