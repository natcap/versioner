virtualenv test_env --clear
source test_env/bin/activate
pip install pyyaml
python setup.py install
python setup.py --version
python -c "import natcap.versioner; print 'FOUND', natcap.versioner.get_version()"
