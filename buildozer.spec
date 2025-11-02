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
android.minapi = 21
android.ndk = 25b
android.archs = armeabi-v7a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Caminhos fixos para o ambiente do GitHub
android.sdk_path = /home/runner/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.accept_sdk_license = True

log_level = 2
warn_on_root = 1
