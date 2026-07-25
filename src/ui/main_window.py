import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import vlc
from ..core.video_loader import VideoLoader
from ..core.proxy_manager import ProxyManager

class VideoPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_loader = VideoLoader()
        self.proxy_manager = ProxyManager()
        self.player = None
        self.current_video = None
        self.is_playing = False
        
        self.setup_ui()
        self.update_proxy_status()
        
        # Atualiza proxies em background
        self.proxy_timer = QTimer()
        self.proxy_timer.timeout.connect(self.update_proxy_status)
        self.proxy_timer.start(30000)  # 30 segundos
        
    def setup_ui(self):
        """Configura a interface"""
        self.setWindowTitle("🎬 Video Player Anônimo - Free")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # --- Topo: URL + Controles ---
        top_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Cole a URL do vídeo aqui...")
        self.url_input.returnPressed.connect(self.play_video)
        top_layout.addWidget(self.url_input)
        
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.play_video)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        top_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        top_layout.addWidget(self.stop_btn)
        
        layout.addLayout(top_layout)
        
        # --- Status Bar ---
        status_layout = QHBoxLayout()
        self.proxy_status = QLabel("🛡️ Proxy: Verificando...")
        self.proxy_status.setStyleSheet("padding: 5px;")
        status_layout.addWidget(self.proxy_status)
        
        self.status_label = QLabel("📊 Aguardando...")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # --- Player ---
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("""
            QFrame {
                background-color: black;
                border: 2px solid #333;
                border-radius: 5px;
            }
        """)
        self.video_frame.setMinimumHeight(400)
        layout.addWidget(self.video_frame)
        
        # --- Controles do Player ---
        controls_layout = QHBoxLayout()
        
        self.play_pause_btn = QPushButton("⏸")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.play_pause_btn.setEnabled(False)
        controls_layout.addWidget(self.play_pause_btn)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.change_volume)
        controls_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("🔊 80%")
        controls_layout.addWidget(self.volume_label)
        
        controls_layout.addStretch()
        
        self.time_label = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.time_label)
        
        layout.addLayout(controls_layout)
        
        # --- Log ---
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 11px;
                border: 1px solid #333;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Inicializa VLC
        self.init_vlc()
        self.log("🎬 Player iniciado!")
        self.log("🔍 Carregando lista de proxies...")
        
    def init_vlc(self):
        """Inicializa o player VLC"""
        try:
            self.instance = vlc.Instance()
            self.player = self.instance.media_player_new()
            self.player.set_hwnd(self.video_frame.winId())
        except Exception as e:
            self.log(f"❌ Erro ao iniciar VLC: {e}")
    
    def play_video(self):
        """Reproduz o vídeo"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Aviso", "Digite uma URL!")
            return
        
        self.log(f"📥 Carregando: {url}")
        self.status_label.setText("📥 Carregando...")
        self.play_btn.setEnabled(False)
        
        # Thread para carregar vídeo
        thread = QThread()
        worker = VideoLoaderWorker(url)
        worker.moveToThread(thread)
        
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.video_loaded.connect(self.on_video_loaded)
        worker.error_occurred.connect(self.on_video_error)
        thread.finished.connect(thread.deleteLater)
        
        thread.start()
        
    def on_video_loaded(self, video_path):
        """Quando o vídeo é carregado"""
        self.current_video = video_path
        self.play_btn.setEnabled(True)
        self.play_pause_btn.setEnabled(True)
        
        # Carrega no VLC
        media = self.instance.media_new(video_path)
        self.player.set_media(media)
        self.player.play()
        self.is_playing = True
        
        self.status_label.setText("▶ Reproduzindo")
        self.play_pause_btn.setText("⏸")
        self.log(f"✅ Reproduzindo: {os.path.basename(video_path)}")
        
        # Atualiza tempo
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def on_video_error(self, error):
        """Erro ao carregar vídeo"""
        self.play_btn.setEnabled(True)
        self.status_label.setText("❌ Erro")
        self.log(f"❌ {error}")
        QMessageBox.critical(self, "Erro", f"Falha ao carregar vídeo:\n{error}")
        
    def toggle_play_pause(self):
        """Alterna play/pause"""
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.play_pause_btn.setText("▶")
            self.status_label.setText("⏸ Pausado")
        else:
            self.player.play()
            self.is_playing = True
            self.play_pause_btn.setText("⏸")
            self.status_label.setText("▶ Reproduzindo")
    
    def stop_video(self):
        """Para o vídeo"""
        if self.player:
            self.player.stop()
        self.is_playing = False
        self.play_pause_btn.setText("▶")
        self.status_label.setText("⏹ Parado")
        self.log("⏹ Vídeo parado")
        
    def change_volume(self, value):
        """Muda o volume"""
        self.player.audio_set_volume(value)
        self.volume_label.setText(f"🔊 {value}%")
    
    def update_time(self):
        """Atualiza o tempo do vídeo"""
        if self.player:
            length = self.player.get_length()
            time = self.player.get_time()
            if length > 0:
                current = f"{time//60000:02d}:{(time%60000)//1000:02d}"
                total = f"{length//60000:02d}:{(length%60000)//1000:02d}"
                self.time_label.setText(f"{current} / {total}")
    
    def update_proxy_status(self):
        """Atualiza status do proxy"""
        proxy = self.proxy_manager.get_proxy()
        if proxy:
            ip = proxy.split('://')[1].split(':')[0]
            self.proxy_status.setText(f"🛡️ Proxy: Ativo ({ip})")
            self.proxy_status.setStyleSheet("color: #4CAF50; padding: 5px;")
            self.log(f"🌐 Proxy ativo: {ip}")
        else:
            self.proxy_status.setText("🛡️ Proxy: Indisponível (Conexão Direta)")
            self.proxy_status.setStyleSheet("color: #FFA500; padding: 5px;")
            self.log("⚠️ Sem proxy - usando conexão direta")
    
    def log(self, message):
        """Adiciona mensagem no log"""
        self.log_text.append(f"[{QDateTime.currentDateTime().toString('hh:mm:ss')}] {message}")
        # Scroll para o final
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """Limpa recursos ao fechar"""
        if self.player:
            self.player.stop()
        self.video_loader.cleanup()
        event.accept()


class VideoLoaderWorker(QObject):
    finished = pyqtSignal()
    video_loaded = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            loader = VideoLoader()
            video_path = loader.get_video_stream(self.url)
            if video_path:
                self.video_loaded.emit(video_path)
            else:
                self.error_occurred.emit("Não foi possível carregar o vídeo")
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()