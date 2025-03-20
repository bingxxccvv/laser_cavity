import numpy as np
from dataclasses import dataclass

@dataclass
class CavityParams:
    """谐振腔参数类"""
    R1: float  # 镜面1的曲率半径
    R2: float  # 镜面2的曲率半径
    L: float   # 腔长
    wavelength: float  # 波长

class LaserCavity:
    def __init__(self, params: CavityParams):
        self.params = params
        self._check_params()
    
    def _check_params(self):
        """检查参数有效性"""
        if self.params.L <= 0:
            raise ValueError("腔长必须为正值")
        if self.params.wavelength <= 0:
            raise ValueError("波长必须为正值")
    
    def get_stability_parameters(self):
        """计算稳定性参数 g1, g2"""
        g1 = 1 - self.params.L / self.params.R1 if self.params.R1 != 0 else 1
        g2 = 1 - self.params.L / self.params.R2 if self.params.R2 != 0 else 1
        return g1, g2
    
    def is_stable(self):
        """判断谐振腔是否稳定"""
        g1, g2 = self.get_stability_parameters()
        stability = g1 * g2
        return 0 <= stability <= 1, stability