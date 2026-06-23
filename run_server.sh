#!/bin/bash
# Script para executar o passeio virtual "Cacau e as Pegadas Perdidas"

# Verificar se Python está instalado
if command -v python &> /dev/null; then
    echo "Iniciando servidor HTTP na porta 8000..."
    echo "Abra http://localhost:8000 no navegador"
    cd "$(dirname "$0")"
    python -m http.server 8000
elif command -v python3 &> /dev/null; then
    echo "Iniciando servidor HTTP na porta 8000..."
    echo "Abra http://localhost:8000 no navegador"
    cd "$(dirname "$0")"
    python3 -m http.server 8000
else
    echo "Python não encontrado. Por favor instale Python ou use um servidor HTTP alternativo."
    exit 1
fi
