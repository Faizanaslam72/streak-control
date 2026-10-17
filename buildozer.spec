[app]

title = Streak Control
package.name = streakcontrol
package.domain = org.streak
source.dir = .
source.include_exts = py,json,png,jpg
version = 1.0.0

requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0
android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.branch = v2024.01.21

# icon / presplash (optional; falls back to defaults if missing)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

[buildozer]
log_level = 2
warn_on_root = 0
