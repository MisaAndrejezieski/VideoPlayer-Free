import logging
from typing import Optional

import yt_dlp

from .proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

class VideoLoader:
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager or ProxyManager()
        self.current_stream = None
        logger.info("🎥 VideoLoader inicializado para streaming")
        
    def get_video_stream(self, url: str) -> Optional[str]:
        """Retorna o URL direto do stream para reprodução."""
        try:
            proxy = self.proxy_manager.get_proxy()
            headers = self.proxy_manager.get_headers()
            
            logger.info(f"🌐 Usando headers: {headers.get('User-Agent', 'N/A')[:50]}...")
            
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'http_headers': headers,
                'socket_timeout': 30,
                'retries': 3,
            }
            
            if proxy:
                ydl_opts['proxy'] = proxy
                logger.info(f"🔒 Usando proxy: {proxy}")
            else:
                logger.warning("⚠️ Sem proxy disponível - usando conexão direta")
            
            logger.info(f"📥 Extraindo stream de: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = self._select_stream_url(info)
                if stream_url:
                    self.current_stream = stream_url
                    logger.info(f"✅ Stream disponível: {stream_url}")
                    return stream_url
                logger.error("❌ Não foi possível obter URL de stream")
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"❌ Erro ao extrair stream: {e}")
            try:
                logger.info("🔄 Tentando fallback sem proxy...")
                ydl_opts.pop('proxy', None)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    stream_url = self._select_stream_url(info)
                    if stream_url:
                        self.current_stream = stream_url
                        logger.info(f"✅ Stream disponível sem proxy: {stream_url}")
                        return stream_url
            except Exception as e2:
                logger.error(f"❌ Fallback falhou: {e2}")
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