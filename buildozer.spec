[app]
title = Analista Esportivo Pro
package.name = analista_esportivo
package.domain = org.sclynter
source.dir = analista_esportivo_app
source.include_exts = py,png,jpg,kv,json
version = 0.1

requirements = python3,kivy,pandas,requests,lxml

orientation = portrait
icon.filename = assets/icon.png

# Versões modernas compatíveis com o GitHub Actions
android.api = 33
android.minapi = 21
android.ndk = 25b

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.arch = armeabi-v7a

# Caminhos fixos para o ambiente do GitHub
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653

log_level = 2
warn_on_root = 1