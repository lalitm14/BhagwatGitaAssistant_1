@echo off
setlocal
cd /d %~dp0\..
python app\query_engine.py "%~1" --config app\config.yaml --answer-language English --document-language Auto --query-language Auto
