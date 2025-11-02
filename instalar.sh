#!/usr/bin/env bash
set -e
echo "Script de build para Analista Esportivo"
echo "ATENCAO: Construir APK no Termux pode falhar por falta de dependências nativas."
echo "Recomendado: usar uma máquina Linux com buildozer + SDK/NDK instalados."
echo ""

if command -v termux-info >/dev/null 2>&1; then
  echo "Detectado Termux. Segue tentativa automática..."
  echo "1) Atualizando e instalando pacotes (pode pedir confirmação)"
  pkg update -y || true
  pkg install -y git python ffmpeg make clang openjdk-17 wget unzip
  pip install --upgrade pip setuptools virtualenv
  pip install --user buildozer
  export PATH=$PATH:~/.local/bin
else
  echo "Não detectado Termux. Presumo ambiente Linux."
  echo "Instale buildozer e dependências no seu Linux e execute: buildozer android debug"
  echo "Para Ubuntu/Debian por exemplo:"
  echo "  sudo apt update && sudo apt install -y python3-pip build-essential git python3-setuptools python3-virtualenv"
  echo "  pip3 install --user buildozer"
  echo "  export PATH=$PATH:~/.local/bin"
fi

echo ""
echo "Preparando diretório e criando ambiente virtual..."
python3 -m venv .venv || true
source .venv/bin/activate || true
pip install --upgrade pip
pip install buildozer
pip install kivy requests pandas

echo "Rodando buildozer (debug)..."
# buildozer pode levar MUITO TEMPO. Se falhar, veja as instruções no README.
buildozer android debug || { echo 'Buildozer falhou. Tente em um Linux com SDK/NDK configurados.'; exit 1; }

echo "Se o build completar, o APK estará em bin/"