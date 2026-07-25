import logging
import os
import tempfile
from typing import Optional

import yt_dlp

from .proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

class VideoLoader:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.temp_dir = tempfile.mkdtemp(prefix='video_player_')
        self.current_video = None
        
    def get_video_stream(self, url: str) -> Optional[str]:
        """Retorna URL do stream com proxy"""
        try:
            # Configuração do yt-dlp
            proxy = self.proxy_manager.get_proxy()
            headers = self.proxy_manager.get_headers()
            
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'headers': headers,
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
            }
            
            # Adiciona proxy se disponível
            if proxy:
                ydl_opts['proxy'] = proxy
                logger.info(f"Usando proxy: {proxy}")
            else:
                logger.warning("Sem proxy disponível - usando conexão direta")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Tenta baixar o vídeo
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                
                if os.path.exists(video_path):
                    self.current_video = video_path
                    logger.info(f"✅ Vídeo carregado: {video_path}")
                    return video_path
                
        except Exception as e:
            logger.error(f"Erro ao carregar vídeo: {e}")
            # Fallback: tenta sem proxy
            try:
                logger.info("Tentando sem proxy...")
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'quiet': True,
                    'no_warnings': True,
                    'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_path = ydl.prepare_filename(info)
                    if os.path.exists(video_path):
                        self.current_video = video_path
                        return video_path
            except Exception as e2:
                logger.error(f"Falha no fallback: {e2}")
        
        return None
    
    def cleanup(self):
        """Limpa arquivos temporários"""
        try:
            if self.current_video and os.path.exists(self.current_video):
                os.remove(self.current_video)
            if os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)
        except:
            pass