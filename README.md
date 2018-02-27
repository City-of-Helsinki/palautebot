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

### Handling feedback from Twitter

* Run `python manage.py handle_twitter_feedback`

### Handling ticket updates in Open311

* Run `python manage.py handle_ticket_updates`

## Settings for the actual bot usage

For Twitter

* TWITTER_CONSUMER_KEY
* TWITTER_CONSUMER_SECRET
* TWITTER_ACCESS_TOKEN
* TWITTER_ACCESS_TOKEN_SECRET
* SEARCH_STRING any tweet found when searching with this string is considered feedback. tested only with hashtags
* TWITTER_USER_RATE_LIMIT_PERIOD (optional, default 60*24 = 1 day) how long period in minutes is used when checking user rate limit
* TWITTER_USER_RATE_LIMIT_AMOUNT (optional, default 5) how many tweets are allowed for a user in the above period

For Open311

* OPEN311_API_KEY
* OPEN311_API_SERVICE_CODE
* OPEN311_API_BASE_URL (in Helsinki: "https://asiointi.hel.fi/palautews/rest/v1/")
* OPEN311_FEEDBACK_URL url of a web page where a single Open311 ticket is displayed, must include {} as a placeholder for the ticket id
  (in Helsinki: "https://www.hel.fi/helsinki/fi/kaupunki-ja-hallinto/osallistu-ja-vaikuta/palaute/nayta-palaute?fid={}") 
* OPEN311_TICKET_POLLING_TIME (optional, default 24*30 = 30 days) how long tickets are polled from Open311 after their latest modification

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
