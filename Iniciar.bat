@echo off
REM ============================================================
REM Build Script para Doguinho Clear Pro
REM Certifique-se de ter o PyInstaller instalado:
REM     pip install pyinstaller
REM ============================================================

echo ========================================
echo Iniciando build do Doguinho Clear Pro...
echo ========================================

taskkill /IM limpeza_gui.exe /F

REM Remove pastas e arquivos de build antigos
IF EXIST build (
    echo Removendo a pasta build antiga...
    rmdir /s /q build
)
IF EXIST dist (
    echo Removendo a pasta dist antiga...
    rmdir /s /q dist
)
IF EXIST Doguinho_Clear.spec (
    echo Removendo o arquivo Doguinho_Clear.spec antigo...
    del /f /q Doguinho_Clear.spec
)

REM Chama o PyInstaller para criar um único executável sem console.
REM Se você tiver um ícone (app.ico), mantenha o parâmetro --icon.
echo ========================================
echo Executando o PyInstaller...
echo ========================================
pyinstaller --onefile --noconsole --uac-admin --icon=icon.ico limpeza_gui.py

IF %errorlevel% NEQ 0 (
    echo ========================================
    echo Build falhou! Verifique os logs e tente novamente.
    echo ========================================
    pause
    exit /b 1
)

echo ========================================
echo Build concluída com sucesso!
echo O executável foi gerado na pasta "dist".
echo ========================================
pause
