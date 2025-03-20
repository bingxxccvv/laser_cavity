import numpy as np
from dataclasses import dataclass
from .cavity_base import CavityParams

@dataclass
class GaussianBeamParams:
    """高斯光束参数类"""
    w0: float      # 束腰半径
    z_R: float     # 瑞利长度
    z: float       # 距离束腰的位置
    wavelength: float  # 波长
    
    @property
    def q_parameter(self):
        """计算复参数q"""
        return self.z + 1j * self.z_R
    
    @property
    def w(self):
        """计算光斑半径"""
        return self.w0 * np.sqrt(1 + (self.z/self.z_R)**2)
    
    @property
    def R(self):
        """计算波前曲率半径"""
        if self.z == 0:
            return float('inf')
        return self.z * (1 + (self.z_R/self.z)**2)
    
    @property
    def gouy_phase(self):
        """计算Gouy相位"""
        return np.arctan2(self.z, self.z_R)

class CavityModeCalculator:
    """谐振腔模式计算器"""
    def __init__(self, cavity_params: CavityParams):
        self.params = cavity_params
        
    def calculate_eigenmode(self):
        """计算谐振腔本征模式参数"""
        L = self.params.L
        R1 = self.params.R1
        R2 = self.params.R2
        wavelength = self.params.wavelength
        
        g1 = 1 - L/R1 if R1 != 0 else 1
        g2 = 1 - L/R2 if R2 != 0 else 1
        
        if abs(g1*g2) > 1:
            raise ValueError("谐振腔不稳定")
            
        denominator = (g1 + g2 - 2 * g1 * g2)**2
        if denominator == 0:
            raise ZeroDivisionError("分母为零，无法计算w0")
        w0 = np.sqrt(wavelength * L / (np.pi) * 
                     np.sqrt((g1 * g2 * (1 - g1 * g2)) / denominator))
        
        z1 = L*(g2*(1-g1))/(g1+g2-2*g1*g2)
        
        z_R = np.pi * w0**2 / wavelength
        
        return GaussianBeamParams(w0=w0, z_R=z_R, z=z1, wavelength=wavelength)