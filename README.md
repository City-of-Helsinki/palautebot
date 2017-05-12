# Palaute-Bot

## Requirements
  - Twitter Account and keys
  - Instagram Account and keys
  - Facebook Account and keys (with valid phone number)
  - Facebook page for palaute-bot

## Assebly for testing
  - Install dependencies `python36 pip install -r requirements.txt`
  - Create Database table `python36 manage.py migrate --settings=project.local_settings.py`
  - Create a file to projects folder called local_settings.py
  - To make it work instantly you can use following names for the keys
    - `TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_TOKEN = ''
TWITTER_ACCESS_TOKEN_SECRET = ''
INSTAGRAM_CLIENT_ID = ''
INSTAGRAM_CLIENT_SECRET = ''
INSTAGRAM_REDIRECT_URI = ''
INSTAGRAM_ACCESS_TOKEN_SCOPE = 'basic comments'
INSTAGRAM_ACCESS_TOKEN = ''
FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''
HELSINKI_API_KEY = ''
SEARCH_STRING = '#ExamleTestHashtag'`
  - Run the script `python36 manage.py palautebot --settings=project.local_settings.py`

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

  - **Instagram**
    - Join to Instagram developer on https://www.instagram.com/developer/
    - Select Manage Clients from top navigation
    - Register a new Client App by filling in the form
    - Select MANAGE from your app's upper right corner
    - **You need the following 2 keys**
      - CLIENT ID
      - CLIENT SECRET
      - Redirect uri
      - Scope = 'basic comments'
          - **For Instagram access token**
            - run python36 manage.py get_instagram_access_token --settings=projects/local_settings
            - follow instructions

  - **Facebook**
    - Create a facebook page for the bot
      - 
    - Join to Facebook Developer on https://developers.facebook.com/
    - Select My Apps (upper right corner)
    - Select Add a New App
    - fill in the needed info
    - **You need the following 2 keys**
      - APP ID
      - APP SECRET


  - **What to do with keys**
    - Paste all keys and info to projects/local_settings.py

  ## Issues

  ### Instagram
  - Publishing via instagram api is limited to 60 comments per hour (https://www.instagram.com/developer/limits/)
  - python-instagram library is not actively mainained (will have to be switched to community version when community version is good enough)
  - All posts have to be public in order to bot to see them.

### Twitter
  - Applications are allowed to make maximum of 350 requests per hour.
  - Querying tweets by hashtag is limited to 100 tweets per query.

## Architecture

## Usage

## Code style

  PEP8

## License

[The MIT Licence](https://opensource.org/licenses/MIT)

