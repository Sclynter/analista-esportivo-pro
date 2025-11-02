Analista Esportivo - pacote pronto
=================================

Conteúdo:
- analista_esportivo_app.py  -> arquivo principal do app (Kivy)
- football.json-master/      -> dados de exemplo (substitua pela sua pasta real, se quiser)
- assets/                    -> icon.png e background.jpg (placeholders)
- buildozer.spec             -> arquivo de configuração para empacotar APK
- instalar.sh                -> script de tentativa de build no Termux / Linux

Uso (Termux):
1) Coloque este ZIP em /storage/emulated/0/Download/ e extraia.
2) Abra Termux e dê permissão: termux-setup-storage
3) cd ~/storage/downloads/analista_esportivo_app_pkg
4) bash instalar.sh
5) Se tudo funcionar, APK aparecerá em bin/
   Caso ocorra erro, recomenda-se usar uma máquina Linux com Buildozer.