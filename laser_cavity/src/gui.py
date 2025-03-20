import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QComboBox, QTabWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from .cavity_base import CavityParams, LaserCavity
from src.gaussian_beam import CavityModeCalculator
from .fox_li import FoxLiCalculator
from .modes import calculate_higher_order_modes

class CavityAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("激光谐振腔分析器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # 创建控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        
        # 添加参数输入
        params = [
            ("R1 (m):", "1.0"),
            ("R2 (m):", "1.0"),
            ("L (m):", "1.0"),
            ("波长 (m):", "1.064e-6")
        ]
        
        self.param_inputs = {}
        for label_text, default_value in params:
            row = QHBoxLayout()
            label = QLabel(label_text)
            input_field = QLineEdit(default_value)
            row.addWidget(label)
            row.addWidget(input_field)
            control_layout.addLayout(row)
            self.param_inputs[label_text] = input_field
        
        # 添加模式选择
        self.plot_type = QComboBox()
        self.plot_type.addItems(["强度分布", "相位分布", "光束参数", "高阶模式"])
        control_layout.addWidget(QLabel("显示类型:"))
        control_layout.addWidget(self.plot_type)
        
        # 添加计算按钮
        calc_button = QPushButton("计算")
        calc_button.clicked.connect(self.calculate)
        control_layout.addWidget(calc_button)
        
        # 添加结果显示区域
        self.result_label = QLabel()
        control_layout.addWidget(self.result_label)
        
        # 添加图形显示区域
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        # 布局
        layout.addWidget(control_panel, stretch=1)
        layout.addWidget(self.canvas, stretch=2)
        
    def calculate(self):
        try:
            params = CavityParams(
                R1=float(self.param_inputs["R1 (m):"].text()),
                R2=float(self.param_inputs["R2 (m):"].text()),
                L=float(self.param_inputs["L (m):"].text()),
                wavelength=float(self.param_inputs["波长 (m):"].text())
            )
            
            cavity = LaserCavity(params)
            stable, stability = cavity.is_stable()
            
            mode_calc = CavityModeCalculator(params)
            gaussian_params = mode_calc.calculate_eigenmode()
            
            size = 10 * gaussian_params.w0
            fox_li = FoxLiCalculator(params.wavelength, params.L, size)
            
            initial_field = np.exp(-(fox_li.X**2 + fox_li.Y**2)/(gaussian_params.w0**2))
            field, loss = fox_li.iterate(initial_field, params.R1, params.R2)
            
            self.result_label.setText(
                f"谐振腔状态: {'稳定' if stable else '不稳定'}\n"
                f"稳定性参数: {stability:.3f}\n"
                f"束腰半径: {gaussian_params.w0*1e6:.2f} μm\n"
                f"单程损耗: {loss*100:.2f}%"
            )
            
            self.plot_results(field, gaussian_params, fox_li, params)
            
        except ValueError as e:
            self.result_label.setText(f"错误: {str(e)}")
    
    def plot_results(self, field, gaussian_params, fox_li, params):
        self.figure.clear()
        plot_type = self.plot_type.currentText()
        
        if plot_type == "强度分布":
            ax = self.figure.add_subplot(111)
            intensity = np.abs(field)**2
            im = ax.imshow(intensity, 
                          extent=[-fox_li.size/2*1e3, fox_li.size/2*1e3, 
                                 -fox_li.size/2*1e3, fox_li.size/2*1e3],
                          cmap='viridis')
            ax.set_xlabel('x (mm)')
            ax.set_ylabel('y (mm)')
            ax.set_title('Pattern Intensity Distribution')
            
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            self.figure.colorbar(im, cax=cax)
            
        elif plot_type == "相位分布":
            ax = self.figure.add_subplot(111)
            phase = np.angle(field)
            im = ax.imshow(phase,
                          extent=[-fox_li.size/2*1e3, fox_li.size/2*1e3,
                                 -fox_li.size/2*1e3, fox_li.size/2*1e3],
                          cmap='hsv')
            ax.set_xlabel('x (mm)')
            ax.set_ylabel('y (mm)')
            ax.set_title('Pattern Phase Distribution')
            
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            self.figure.colorbar(im, cax=cax)
            
        elif plot_type == "光束参数":
            ax = self.figure.add_subplot(111)
            z = np.linspace(-params.L/2, params.L/2, 100)
            w = gaussian_params.w0 * np.sqrt(1 + (z/gaussian_params.z_R)**2)
            
            ax.plot(z*1e3, w*1e6)
            ax.set_xlabel('z (mm)')
            ax.set_ylabel('Beam Radius(μm)')
            ax.set_title('Beam Propagation Characteristics')
            ax.grid(True)
            
        elif plot_type == "高阶模式":
            modes, _ = calculate_higher_order_modes(params, fox_li, n_max=2, m_max=2)
            
            fig = self.figure
            fig.set_size_inches(10, 8)
            for idx, ((n, m), mode) in enumerate(modes.items(), 1):
                ax = fig.add_subplot(2, 2, idx)
                im = ax.imshow(np.abs(mode)**2, 
                             extent=[-fox_li.size/2*1e3, fox_li.size/2*1e3,
                                    -fox_li.size/2*1e3, fox_li.size/2*1e3],
                             cmap='viridis')
                ax.set_title(f'HG{n}{m}Pattern')
                ax.set_xlabel('x (mm)')
                ax.set_ylabel('y (mm)')
                
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="5%", pad=0.05)
                fig.colorbar(im, cax=cax)
            
            fig.tight_layout()
        
        self.canvas.draw()