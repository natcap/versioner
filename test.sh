if [ "$1" = "build" ]
then
    virtualenv test_env --clear --system-site-packages
    source test_env/bin/activate
    python setup.py install
    pushd ../invest
    python setup.py install
    popd
else
    source test_env/bin/activate
    python setup.py install
fi

python -c "import natcap.versioner; print 'FOUND', natcap.versioner.get_version('natcap.invest')"
python -c "import natcap.invest; print 'INVEST', natcap.invest.__version__"
