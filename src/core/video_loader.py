import logging
import os
import shutil
import tempfile
from typing import Optional

import yt_dlp

from .proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

class VideoLoader:
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager or ProxyManager()
        self.temp_dir = tempfile.mkdtemp(prefix='video_player_')
        self.current_video = None
        logger.info(f"📁 Pasta temporária: {self.temp_dir}")
        
    def get_video_stream(self, url: str) -> Optional[str]:
        """Retorna o caminho do vídeo baixado"""
        try:
            proxy = self.proxy_manager.get_proxy()
            headers = self.proxy_manager.get_headers()
            
            logger.info(f"🌐 Usando headers: {headers.get('User-Agent', 'N/A')[:50]}...")
            
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'quiet': False,  # Muda para False para ver mais detalhes
                'no_warnings': False,
                'extract_flat': False,
                'headers': headers,
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'socket_timeout': 30,  # Timeout maior
                'retries': 3,
            }
            
            if proxy:
                ydl_opts['proxy'] = proxy
                logger.info(f"🔒 Usando proxy: {proxy}")
            else:
                logger.warning("⚠️ Sem proxy disponível - usando conexão direta")
            
            logger.info(f"📥 Baixando vídeo de: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                
                logger.info(f"📁 Arquivo gerado: {video_path}")
                
                if os.path.exists(video_path):
                    self.current_video = video_path
                    logger.info(f"✅ Vídeo carregado com sucesso!")
                    return video_path
                else:
                    logger.error(f"❌ Arquivo não encontrado: {video_path}")
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"❌ Erro de download: {e}")
            # Fallback: tenta sem proxy
            try:
                logger.info("🔄 Tentando sem proxy...")
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'quiet': False,
                    'no_warnings': False,
                    'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                    'socket_timeout': 30,
                    'retries': 3,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_path = ydl.prepare_filename(info)
                    if os.path.exists(video_path):
                        self.current_video = video_path
                        logger.info(f"✅ Vídeo carregado sem proxy!")
                        return video_path
            except Exception as e2:
                logger.error(f"❌ Falha no fallback: {e2}")
        except Exception as e:
            logger.error(f"❌ Erro geral: {e}")
        
        return None
    
    def cleanup(self):
        """Limpa arquivos temporários"""
        try:
            if self.current_video and os.path.exists(self.current_video):
                os.remove(self.current_video)
                logger.info(f"🗑️ Arquivo removido: {self.current_video}")
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                logger.info(f"🗑️ Pasta removida: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao limpar cache: {e}")