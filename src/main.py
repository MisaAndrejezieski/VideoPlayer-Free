import logging
import os
import sys

from dotenv import load_dotenv
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Carrega variáveis de ambiente
load_dotenv()

# Configura logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adiciona src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# CORREÇÃO: Import absoluto
from ui.main_window import VideoPlayerWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = VideoPlayerWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()