virtualenv test_env --clear
source test_env/bin/activate
python setup.py install
python setup.py --version
