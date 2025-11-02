[app]
title = Analista Esportivo Pro
package.name = analista_esportivo
package.domain = org.sclynter
source.dir = src/analista_esportivo
source.include_exts = py,png,jpg,kv,json
version = 0.1

requirements = python3,kivy,pandas,requests,lxml
orientation = portrait
icon.filename = assets/icon.png

android.api = 33
# MANTENHA ESTE VALOR: Necessário para pacotes modernos.
android.minapi = 24
android.archs = armeabi-v7a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# FIX CRÍTICO: Força o uso da branch P4A mais estável para evitar o erro 'autopoint' na compilação do lxml/pandas.
p4a.branch = develop

android.accept_sdk_license = True
p4a_ignore_setup_py = True

log_level = 2
warn_on_root = 1
