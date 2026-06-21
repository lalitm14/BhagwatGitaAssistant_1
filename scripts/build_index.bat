@echo off
setlocal
cd /d %~dp0\..
python app\build_index.py --config app\config.yaml
