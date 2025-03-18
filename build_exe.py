import PyInstaller.__main__
import os

# Get the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'swiper.py',
    '--name=FileSwiper',
    '--onefile',
    '--windowed',
    '--icon=app_icon.ico',
    '--add-data=app_icon.ico;.',
    '--clean',
    f'--workpath={os.path.join(script_dir, "build")}',
    f'--distpath={os.path.join(script_dir, "dist")}',
    '--noconfirm',
]) 