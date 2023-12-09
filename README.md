# EasyChatGPT
This repo is unofficial ChatGPT api.

### Usage
```python
from EasyChatGPT import *

config = ChatGPTConfig(
	chromedriver_path="path/to/chromedriver.exe",
	chrome_path=r'path/to/chrome.exe'
	#token_folder: str = 'folder/with/your/additional/files',
	#session_token="could be 'None', but you would have to login in your openai account",
	#chrome_args=['--some', '--args']
)

api = ChatGPT(config=config)
api.get_last_chat()

response = api.send_message('Do something')
print(response)

response = api.regenerate_last_response()
print(response)
```

## Insipration

This project is inspired by

-   [ChatGPT](https://github.com/acheong08/ChatGPT)
-   [chatgpt-api](https://github.com/transitive-bullshit/chatgpt-api)
-   [pyChatGPT](https://github.com/terry3041/pyChatGPT)
