TOKEN='' # Bot token

REQUEST_KWARGS={
    'proxy_url': '', # Put url in '' 
    'urllib3_proxy_kwargs': {
        'assert_hostname': 'False',
        'cert_reqs': 'CERT_NONE'
    }
}

HELLO_MESSAGE = ("Welcome to our News Search Bot!"
                 "This bot can read news for you!"
                 "It collects all the recent news from the internet"
                 "and analyses it. You can ask it to show you"
                 "the news with specific entity. For example,"
                 "type in some city name in Russian.")

WRONG_LANG_MESSAGE = "Please, our bot works only for Russian language..."

MODEL_PATH = '' # Path to model
