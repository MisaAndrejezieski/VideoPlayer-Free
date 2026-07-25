@echo off
title Video Player
color 0A

echo ========================================
echo  🎬 Video Player Anonimo
echo ========================================
echo.

if not exist ".venv" (
    echo ⚠️  .venv nao encontrado!
    echo Execute setup.bat primeiro
    pause
    exit /b 1
)

echo 🔧 Ativando .venv...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar .venv
    pause
    exit /b 1
)
echo ✅ .venv ativado!
echo.

echo 🚀 Iniciando Video Player...
echo ========================================
echo.

REM CORREÇÃO: Vai para a pasta src e roda
cd src
python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo  ❌ Programa fechou com erro!
    echo  Verifique as mensagens acima.
    echo ========================================
    pause
)