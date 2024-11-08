[app]

# Project name and package details
title = Springle
package.name = springle
package.domain = com.jstumfoll2

# Source code location and included files
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = assets/*,images/*,fonts/*
source.exclude_dirs = tests, bin, .git, __pycache__

# Application versioning
version = 0.1
version.regex = __version__ = '(.*)' 
version.filename = %(source.dir)s/app/main.py

# Requirements
requirements = python3,kivy,pillow,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf

# Android specific configurations
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.arch = arm64-v8a

# Application configuration
orientation = portrait
fullscreen = 0

# Icons and presplash
#android.presplash_color = #FFFFFF
#icon.filename = %(source.dir)s/data/icon.png
#presplash.filename = %(source.dir)s/data/presplash.png

# Control debug output in the application
android.logcat_filters = *:S python:D

[buildozer]
# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2
warn_on_root = 1