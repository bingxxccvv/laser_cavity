# 导入必要的系统模块
import sys  # 提供Python运行时环境的变量和函数

# 从我们的src目录导入GUI类
from src.gui import CavityAnalyzerGUI  # 导入我们之前创建的GUI类

# 导入PyQt5的QApplication类，这是Qt应用程序的基础
from PyQt5.QtWidgets import QApplication

# 确保代码只在直接运行此文件时执行，而不是在导入时执行
if __name__ == "__main__":
    # 创建QApplication实例
    # sys.argv包含命令行参数，QApplication需要这个来初始化
    app = QApplication(sys.argv)
    
    # 创建我们的主窗口实例
    window = CavityAnalyzerGUI()
    
    # 显示窗口
    window.show()
    
    # 启动应用程序的主事件循环
    # app.exec_()会一直运行，直到窗口被关闭
    # sys.exit()确保程序在窗口关闭时正确退出
    sys.exit(app.exec_())