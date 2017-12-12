# Palaute-Bot

## Requirements
  - Twitter Account and keys
  - Instagram Account and keys
  - Facebook Account and keys (with valid phone number)
  - Facebook page for palaute-bot

## Assebly for testing
  - Install dependencies `python pip install -r requirements.txt`
  - Create Database table `python manage.py migrate`
  - Create a file to projects folder called local_settings.py
  - To make it work instantly you can use following names for the keys
    - `TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_TOKEN = ''
TWITTER_ACCESS_TOKEN_SECRET = ''
INSTAGRAM_CLIENT_ID = ''
INSTAGRAM_CLIENT_SECRET = ''
INSTAGRAM_REDIRECT_URI = 'http://palautebot.local/'
INSTAGRAM_ACCESS_TOKEN_SCOPE = 'basic comments'
INSTAGRAM_ACCESS_TOKEN = ''
FACEBOOK_PAGE_ID= ''
FACEBOOK_PAGE_ACCESS_TOKEN = ''
HELSINKI_API_KEY = ''
SEARCH_STRING = '#ExamleTestHashtag'`
  - Run the script `python manage.py palautebot`

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
      - You need the page id from url 
    - Join to Facebook Developer on https://developers.facebook.com/
    - Select My Apps (upper right corner)
    - Select Add a New App
    - fill in the needed info
    - Head over to the Facebook Graph API Explorer https://developers.facebook.com/tools/explorer/
      - On the top right, select the FB App you created from the "Application" drop down list
      - Click "Get User Access Token"
      - Add the manage_pages and publish_pages permission in the checkbox list
      - Click info icon at the left side of generated token
      - Click open in Access Token Tool
      - Click Extend Access Token and Copy the extended token
      - Return to Graph API Explorer in another tab
      - Replace user access token in the access token field with the generated extended user access token
      - Select your page at the dropdown (right side of access token field)
      - Click info icon at the left side of generated token and open in access token tool
      - You should now see that token Expires=Never
      - **You need the following 2 keys**
        - Access Token (Page access token)
        - Page ID

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

### Facebook
  - Stable version (2.00) of Facebook-sdk does not support the latest facebook graph version. There's an alpha version of facebook-sdk (3.00) that supports the latest.
  - 
## Architecture

## Usage

## Code style

  PEP8

## License

[The MIT Licence](https://opensource.org/licenses/MIT)

