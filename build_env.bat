conda create -p ./venv python=3.8 --y
conda install -n ./venv pip --y
conda activate ./venv
pip install -r requirements.txt
conda info
