[app]

# 应用名称
title = 医学AR+VR教程

# 包名
package.name = medicaltutorial

# 包域名
package.domain = org.medical

# 源代码目录
source.dir = .

# 源代码包含的文件类型
source.include_exts = py,png,jpg,kv,atlas,mp4

# 版本号
version = 1.0.0

# 所需权限
requirements = python3,kivy,plyer,android

# 支持的Android版本
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# 屏幕方向 (landscape或portrait)
orientation = landscape

# 是否全屏
fullscreen = 0

# 图标
# icon.filename = icon.png

# 启动画面
# presplash.filename = presplash.png

# 权限
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# 架构
android.archs = arm64-v8a,armeabi-v7a

# 是否允许备份
android.allow_backup = True

# 应用主题
android.theme = "@android:style/Theme.NoTitleBar"

[buildozer]

# 日志级别 (0=error, 1=warning, 2=info, 3=debug)
log_level = 2

# 警告作为错误
warn_on_root = 1
