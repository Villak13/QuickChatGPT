import time
from enum import Enum
import undetected_chromedriver as uc
from selenium.webdriver import ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ChromeOptions


class Selectors(Enum):
	alpha = (By.CSS_SELECTOR, '#__next > div > div.flex.w-full.items-center.justify-between.bg-blue-950.p-3.text-white > div > div > button')
	textinput = (By.XPATH, '//textarea[@id="prompt-textarea"]')
	conversations = (By.CSS_SELECTOR, '#__next > div.relative.z-0.flex.h-full.w-full.overflow-hidden > div.dark.flex-shrink-0.overflow-x-hidden.bg-black > div > div > div > div > nav > div.flex-col.flex-1.transition-opacity.duration-500.-mr-2.pr-2.overflow-y-auto > div.flex.flex-col.gap-2.pb-2.text-sm > div > span:nth-child(1) a')
	new_chat = (By.LINK_TEXT, 'New chat')
	chatgpt_small_response = (By.XPATH, '//div[contains(@class, "markdown prose w-full break-words dark:prose-invert")]')
	continue_generating = (By.XPATH, '//*[@id="__next"]/div[1]/div[2]/main/div[2]/div[2]/form/div/div[1]/div/div[2]/div/button')
	go_down_button = (By.XPATH, '//*[@id="__next"]/div[1]/div[2]/main/div[2]/div[1]/div/div/div/button')
	running_indicator = (By.XPATH, '//*[@id="__next"]/div[1]/div[2]/main/div[2]/div[2]/form/div/div/div/div/div/div/button')
	error_announcement = (By.XPATH, '//*[@id="__next"]/div[1]/div[2]/main/div[2]/div[1]/div/div/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div[2]')
	tips_window = (By.CSS_SELECTOR, '.relative.col-auto.col-start-2.row-auto.row-start-2.w-full.rounded-xl.text-left.shadow-xl.transition-all button')
	regenerate_on_error = (By.XPATH, '//*[@id="__next"]/div[1]/div[2]/main/div[2]/div[2]/div[1]/div[2]/button')


def login_manually(chromedriver_path, options, token_folder):
	print('Login to openai using your account')
	time.sleep(5)
	
	driver = uc.Chrome(options=options, service=ChromeService(executable_path=chromedriver_path))
	driver.get('https://chat.openai.com/auth/login')

	WebDriverWait(driver, 2000).until(lambda _driver: _driver.current_url.endswith('chat.openai.com/'))
	token = driver.get_cookie('__Secure-next-auth.session-token')['value']
	open(f'{token_folder}/session_token.txt', 'w').write(token)
	driver.close()
	print('Done! Now your token is saved in file session_token.txt')
	return token


class Versions(Enum):
	gpt3_5__turbo = dict(name="gpt-3.5-turbo", max_input_tokens=2048)
	
	def __str__(self):
		return self.value['name']
	
	def __int__(self):
		return self.value['max_input_tokens']


class ChatGPTConfig:
	def __init__(self, chromedriver_path, chrome_path=None, token_folder: str = '.', session_token=None, chatgpt_version: Versions = Versions.gpt3_5__turbo, chrome_args=None):
		try:
			open(f'{token_folder}/session_token.txt', 'x')
		except FileExistsError:
			pass
		options = ChromeOptions()
		for arg in chrome_args or ['--headless', "--mute-audio"]:
			options.add_argument(arg)
		if chrome_path:
			options.binary_location = chrome_path
		self.options = options
		
		self.session_token = session_token or open(f'{token_folder}/session_token.txt', 'r').read() or login_manually(chromedriver_path, options, token_folder)
		self.chromedriver_path = chromedriver_path
		self.chatgpt_version = chatgpt_version

