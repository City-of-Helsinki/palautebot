# Palaute-Bot

## Prerequisites

* PostgreSQL (>= 9.5) (a couple of older versions probably work as well)
* Python (>= 3.4)
* Twitter account and keys
* Open311 keys

## Creating a Python virtualenv

First it is highly recommended to create a Python virtualenv for the project. There are many ways to do this, using vanilla Python:

* Run `python -m venv venv`

## Python requirements

Python requirements are handled with [pip-tools](https://github.com/jazzband/pip-tools). To install it

* Run `pip install pip-tools`

### Creating / updating Python requirements files (needed only when the requirements are changed)

* Run `pip-compile`
* For development requirements run `pip-compile requirements-dev.in`

### Installing Python requirements

* Run `pip-sync`
* To install also development requirements instead run `pip-sync requirements.txt requirements-dev.txt`

## Database

To setup a database compatible with the default database settings:

    sudo -u postgres createuser -P -R -S palautebot  # use password `palautebot`
    sudo -u postgres createdb -O palautebot palautebot

## Django configuration

Environment variables are used to customize configuration in `palautebot/settings.py`. If you wish to override any
settings, you can place them in a local `.env` file which will automatically be sourced when Django imports
the settings file.

Alternatively you can create a `local_settings.py` which is executed at the end of the `palautebot/settings.py` in the
same context so that the variables defined in the settings are available.

## Running development environment

* Enable debug `echo 'DEBUG=True' >> .env`
* Run `python manage.py migrate`
* Run `python manage.py runserver` (admin UI will be accessible at http://localhost:8000/admin)

## Running the bot

* Run `python manage.py palautebot`

## Settings needed for the actual bot usage

For Twitter

    TWITTER_CONSUMER_KEY
    TWITTER_CONSUMER_SECRET
    TWITTER_ACCESS_TOKEN
    TWITTER_ACCESS_TOKEN_SECRET
    SEARCH_STRING

For Open311

    OPEN311_API_KEY
    OPEN311_API_SERVICE_CODE
    OPEN311_POST_API_URL

## Getting the keys
  - **Twitter**
    - Join to Twitter developer on https://dev.twitter.com/
    - Go to My Apps
    - Register new App by filling in the form
    - Open My Apps and select the App that you added
    - Select Keys and Access Tokens tab
    - Generate new access token at the bottom of the page
    - **You need the following 4 keys**
      - Consumer Key (API Key)
      - Consumer Secret (API Secret)
      - Access Token
      - Access Token Secret
  - **Open311** **TODO**

## Issues

### Twitter
  - Applications are allowed to make maximum of 350 requests per hour.
  - Querying tweets by hashtag is limited to 100 tweets per query.

## License

[The MIT Licence](https://opensource.org/licenses/MIT)
