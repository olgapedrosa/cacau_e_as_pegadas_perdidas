@echo off
REM Script de instalação para Windows
REM Execute este arquivo para instalar as dependências do projeto

echo.
echo ====================================================
echo INSTALACAO - Cacau e as Pegadas Perdidas
echo ====================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH
    echo Por favor, instale Python 3.8 ou superior de python.org
    echo e adicione ao PATH
    pause
    exit /b 1
)

echo [1/3] Atualizando pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [2/3] Instalando dependencias...
pip install -r requirements.txt

echo.
echo [3/3] Verificando instalacao...
python -c "import pygame, numpy, OpenGL; print('OK: Todas as dependencias instaladas')" || (
    echo ERRO: Problema na instalacao
    pause
    exit /b 1
)

echo.
echo ====================================================
echo SUCESSO! Dependencias instaladas com sucesso
echo ====================================================
echo.
echo Para executar o programa:
echo   python main.py
echo.
pause
