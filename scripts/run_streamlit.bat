@echo off
setlocal
cd /d %~dp0\..
streamlit run app\streamlit_app.py
