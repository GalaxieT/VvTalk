CALL conda install -c conda-forge montreal-forced-aligner -y
pip install -r requirements.txt
pip install setup_install\PyAudio-0.2.11-cp38-cp38-win_amd64.whl
cd setup_install/huaweicloud-python-sdk-sis-1.7.1
python setup.py install
cd ..
cd ..