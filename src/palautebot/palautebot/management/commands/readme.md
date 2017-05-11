# Palaute-Bot Documents

## Requirements
  - Twitter Account and keys
  - Instagram Account and keys
  - Facebook Account and keys (with valid phone number)
  - Facebook page for palaute-bot


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

  ## Issues

  ### Instagram
  - Publishing via instagram api is limited to 60 comments per hour (https://www.instagram.com/developer/limits/)
  - python-instagram library is not actively mainained (will have to be switched to community version when community version is good enough)
  - All posts have to be public in order to bot to see them.

### Twitter
  - Applications are allowed to make maximum of 350 requests per hour.
  - Querying tweets by hashtag is limited to 100 tweets per query.