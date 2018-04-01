# Twitter Spy

Retrieves specified tweets count (up to ~3200 - Twitter API limit) of a user and tries to understand main topics of his/her posts with `pytextrank` (topic = keyword).

### Prerequisites

`python 3`, `pip3` and `virtualenv` should be installed

Also, `envs.sh` file should be created with Twitter API credentials:
```
export CONSUMER_KEY=...
export CONSUMER_SECRET=...
export ACCESS_TOKEN_KEY=...
export ACCESS_TOKEN_SECRET=...
```

### Installing

```
virtualenv venv
source venv/bin/activate
source envs.sh
pip3 install -r requirements.txt
python3 -m spacy download en
```

### Running

```
python3 twitter_spy username 200
```
