import logging
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Configura logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adiciona src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import VideoPlayerWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = VideoPlayerWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()