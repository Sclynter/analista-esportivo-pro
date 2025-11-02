[app]
title = Analista Esportivo Pro
package.name = analista_esportivo
package.domain = org.sclynter

# Caminho onde está o __main__.py
source.dir = src/analista_esportivo
source.include_exts = py,png,jpg,kv,json

# Arquivo principal da aplicação
main = __main__.py

version = 0.1
requirements = python3,kivy,pandas,requests,lxml

orientation = portrait
icon.filename = assets/icon.png

# Versões compatíveis com GitHub Actions
android.api = 33
android.minapi = 21
android.ndk = 25b

# Permissões do app
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.arch = armeabi-v7a

# Caminhos fixos para o ambiente do GitHub Actions
android.sdk_path = /home/runner/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653

# Logs e comportamento
log_level = 2
warn_on_root = 1
