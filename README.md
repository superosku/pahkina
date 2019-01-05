# Pahkina

## Running with docker

Make sure docker is installed

Build docker container (Note that you have to rebuild after changes)

```
docker build -t pahkina .
```

Running tests

```
docker run -it pahkina py.test
```

Running the script

```
docker run -it pahkina python main.py
```

Running the script with defined output and input files (Note that input file should have empty line at the end so the script knows when to stop)

```
docker run -i pahkina python main.py < dataset.json > output.json
```

## Running without docker

Make sure `python3.7` is installed

Create virtual environment

```
python3.7 -m venv ./venv
```

Activate virtual environment

```
source venv/bin/activate
```

Install requirements

```
pip install -r requirements.txt
```

Make sure your local path is in pythonpath

```
export PYTHONPATH=$PYTHONPATH:/path/to/your/current/folder/
```

Run unit tests

```
py.test
```

Run the script

```
python main.py < dataset.json > output.json
```
