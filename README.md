# Django Chat

This is a simple chat room built using Django Channels.

**Demo [here](https://chat.ploggingdev.com/)**

Note : This demo site will removed after a few days.

Setup instructions on Ubuntu 16.04:

Follow this [guide](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04) for the initial server setup.

Update package index :

```
sudo apt-get update
```

Install dependencies :

```
sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx
```

Database setup :

```
sudo -u postgres psql

CREATE DATABASE djangochat;

CREATE USER djangochatuser WITH PASSWORD 'YOUR_PASSWORD';

ALTER ROLE djangochatuser SET client_encoding TO 'utf8';

ALTER ROLE djangochatuser SET default_transaction_isolation TO 'read committed';

ALTER ROLE djangochatuser SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE djangochat TO djangochatuser;

\q
```

Setup Django project :

```
git clone https://github.com/ploggingdev/djangochat.git

sudo apt install python3-venv

cd djangochat

mkdir venv

python3 -m venv venv/djangochat

source venv/djangochat/bin/activate

pip install -r requirements.txt

pip install --upgrade pip
```

Add environment variables :

```
sudo nano ~/.bashrc

#append the following to the end of the file

export djangochat_secret_key="SECRET_KEY"

export djangochat_db_name="djangochat"

export djangochat_db_user="djangochatuser"

export djangochat_db_password="YOUR_PASSWORD"

export djangochat_postmark_token="POSTMARK_TOKEN"

export DJANGO_SETTINGS_MODULE=djangochat.settings
```

Source the env variables :

```
deactivate

source ~/.bashrc

source venv/djangochat/bin/activate
```

Perform database migration : 

```
python manage.py migrate
```

Install redis by following this [guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04).

Create Django superuser :

```
python manage.py createsuperuser
```

Configure django-channels-presence pruning of websocket connections (this is necessary to remove inactive websocket connections) :

Go to the `/admin/django_celery_beat/periodictask/add/` panel and add a custom task `channels_presence.tasks.prune_presence` with an interval of your choice. I used 60 seconds for testing purposes.

Start the development server :

```
python manage.py runserver
```

Start celery :

```
celery -A chatdemo beat -l info -S django
```

Visit the local development server at `127.0.0.1:8000` to test the site.