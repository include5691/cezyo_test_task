# cezyo_test_task
Test task for Cezyo - mini shop app

## Setup

### Make sure you have running postgresql server
```shell
sudo systemctl status postgresql
```
If not, install via [link](https://www.postgresql.org/download/)

### Clone repository
```shell
git clone git@github.com:include5691/cezyo_test_task.git
cd cezyo_test_task
```

### Create and activate venv
```shell
python3 -m venv .venv
source .venv/bin/activate # for bash
```

### Install requirements
```shell
pip install -r requirements.txt
```

### Create and fulfill .env file with database url
__Format:__  
DATABASE_URL="postgresql+psycopg2://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>"

### Perform alembic migration
```shell
cd src
alembic upgrade head
```
__NOTE:__ The test data are included in the migration file

### Return to repo root and run the app
```shell
cd ..
uvicorn src.main:app --port 8000
```