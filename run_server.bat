@echo off
REM Script para executar o passeio virtual "Cacau e as Pegadas Perdidas" no Windows

setlocal enabledelayedexpansion

echo.
echo ====================================
echo Cacau e as Pegadas Perdidas
echo Passeio Virtual 3D
echo ====================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python não encontrado no PATH
    echo Por favor, instale Python 3 ou adicione-o ao PATH
    pause
    exit /b 1
)

echo Iniciando servidor HTTP...
echo Porta: 8000
echo.
echo Abra seu navegador em: http://localhost:8000
echo.
echo Controles:
echo   W/Seta para cima  - Andar para frente
echo   S/Seta para baixo - Andar para trás
echo   A/Seta esquerda   - Andar para esquerda
echo   D/Seta direita    - Andar para direita
echo   Mouse            - Olhar em volta (clique para ativar)
echo.

python -m http.server 8000

if %errorlevel% neq 0 (
    echo.
    echo Erro ao iniciar o servidor
    pause
    exit /b 1
)

pause
