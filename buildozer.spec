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
# MUDANÇA CRÍTICA: Aumentado para 24 para resolver problemas de compilação de pandas/lxml.
android.minapi = 24
android.archs = armeabi-v7a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# O ANDROID_HOME é definido no workflow do GitHub Actions.
android.accept_sdk_license = True

# Isso pode ajudar com dependências complexas.
p4a_ignore_setup_py = True

log_level = 2
warn_on_root = 1
