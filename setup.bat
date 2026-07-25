@echo off
echo ========================================
echo  🎬 Video Player - Setup
echo ========================================
echo.

REM Verifica Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado!
    echo Instale o Python 3.8+ em: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python: 
python --version
echo.

REM Cria .venv
echo [2/4] Criando ambiente virtual...
if exist .venv (
    echo ⚠️  .venv ja existe. Recriando...
    rmdir /s /q .venv
)
python -m venv .venv
echo ✅ .venv criado!
echo.

REM Instala dependências
echo [3/4] Instalando dependencias...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Dependencias instaladas!
echo.

REM Testa instalação
echo [4/4] Testando instalacao...
python -c "import yt_dlp, vlc, PyQt5" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Erro em alguma biblioteca
    echo Tente: pip install --upgrade yt-dlp python-vlc PyQt5
) else (
    echo ✅ Tudo OK!
)
echo.

echo ========================================
echo  ✅ SETUP CONCLUIDO!
echo ========================================
echo.
echo Para rodar: run.bat
echo.
pause