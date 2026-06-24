#!/bin/bash

# Script de instalação para Linux/Mac
# Execute: chmod +x setup.sh && ./setup.sh

echo ""
echo "===================================================="
echo "INSTALAÇÃO - Cacau e as Pegadas Perdidas"
echo "===================================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não encontrado no PATH"
    echo "Por favor, instale Python 3.8 ou superior"
    exit 1
fi

echo "Python encontrado: $(python3 --version)"
echo ""

echo "[1/3] Atualizando pip..."
python3 -m pip install --upgrade pip setuptools wheel

echo ""
echo "[2/3] Instalando dependências..."
python3 -m pip install -r requirements.txt

echo ""
echo "[3/3] Verificando instalação..."
python3 -c "import pygame, numpy, OpenGL; print('✓ OK: Todas as dependências instaladas')" || {
    echo "✗ ERRO: Problema na instalação"
    exit 1
}

echo ""
echo "===================================================="
echo "✓ SUCESSO! Dependências instaladas com sucesso"
echo "===================================================="
echo ""
echo "Para executar o programa:"
echo "  python3 main.py"
echo ""
