cd %~dp0
cd ../
python -m pip uninstall revChatGPT -y
python setup.py install
