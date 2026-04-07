[app]

title = 医学AR+VR教程
package.name = medicalarvr
package.domain = org.medical
source.dir = .
source.include_exts = py,png,jpg,jpeg,atlas,json,txt
version = 1.0.0

requirements = python3,kivy,pillow
orientation = landscape
fullscreen = 0

android.api = 33
android.minapi = 24
android.archs = arm64-v8a

android.permissions = INTERNET
android.allow_backup = False
android.theme = "@android:style/Theme.NoTitleBar"
android.add_assets = assets/source

[buildozer]

log_level = 2
warn_on_root = 1
