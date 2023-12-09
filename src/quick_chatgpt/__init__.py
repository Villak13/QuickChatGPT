
        self.chatgpt_chat_url = 'https://chat.openai.com/chat'
        
        self.__init_browser(config.options)
        self.change_session_token(config.session_token)
        self.driver.get(f'{self.chatgpt_chat_url}/')
        self.__remove_blocking_elements()

    def __init_browser(self, chrome_options):
        try:
            self.driver = uc.Chrome(driver_executable_path=self.__chromedriver_path, options=chrome_options)
        except TypeError as e:
            if str(e) == 'expected str, bytes or os.PathLike object, not NoneType':
                raise ValueError('Chrome installation not found')
            raise e
        
    def __remove_blocking_elements(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(Selectors.textinput.value))
        except TimeoutException:
            raise BaseException('Probably bad token, try to delete your session_token.txt file')
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(Selectors.tips_window.value))
        except TimeoutException:
            pass
        try:
            alpha = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(Selectors.alpha.value))
            alpha.find_element(By.XPATH, '../../../button').click()
            WebDriverWait(self.driver, 30).until_not(EC.presence_of_element_located(Selectors.alpha.value))
            time.sleep(1)
        except TimeoutException:
            pass

    def send_message(self, prompt):
        self.__send_text(prompt)
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(Selectors.go_down_button.value)).click()
        except TimeoutException:
            pass
        self.__wait_for_full_response()
        return self.__get_response()
    
    def regenerate_last_response(self):
        try:
            small_response = self.driver.find_elements(*Selectors.chatgpt_small_response.value)[-1]
        except IndexError:
            return ''
        
        small_response.find_element(By.XPATH, '../../../div[2]').find_element(By.CSS_SELECTOR, 'div>button:has(div)').click()
        self.__wait_for_full_response()
        return self.__get_response()
    
    def __send_text(self, text):
        # TODO max input characters amount
        # if len(list(text)) > int(self.__chatgpt_version):
        #     print(f'Message should have less than {int(self.__chatgpt_version)} characters!')
        textarea = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(Selectors.textinput.value))
        self.driver.execute_script('arguments[0].setRangeText(arguments[1], 0, 0, "select");', textarea, text)
        textarea.click()
        textarea.send_keys(' ')
        textarea.send_keys(Keys.BACKSPACE)
        text_submit = textarea.find_element(By.XPATH, '../button')
        self.driver.execute_script('arguments[0].click()', text_submit)
        
    def __wait_for_full_response(self):
        while 1:
            WebDriverWait(self.driver, 200).until_not(EC.presence_of_element_located(Selectors.running_indicator.value))
            try:
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(Selectors.continue_generating.value)).click()
            except TimeoutException:
                break
            
    def __get_response(self) -> str:
        try:
            # You've reached our limit of messages per hour.
            # or
            # The message you submitted was too long, please reload the conversation and submit something shorter.
            raise BaseException(self.driver.find_element(*Selectors.error_announcement.value).text.split('.')[0])
        except NoSuchElementException:
            try:
                self.driver.find_element(*Selectors.regenerate_on_error.value).click()
            except NoSuchElementException:
                pass
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(Selectors.chatgpt_small_response.value)).click()

        response = self.driver.find_elements(*Selectors.chatgpt_small_response.value)[-1]
        return markdownify(response.get_attribute('innerHTML')).replace('Copy code`', '`').strip()
    
    def get_last_chat(self):
        self.driver.find_element(*Selectors.conversations.value).click()
    
    def create_new_chat(self):
        self.driver.find_element(*Selectors.new_chat.value).click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(Selectors.textinput.value))
        
    def reflash_page(self):
        self.driver.refresh()
        
    def load_chat(self, chat_id: str):
        self.driver.get(f'https://chat.openai.com/c/{chat_id}')
        
    def change_session_token(self, session_token):
        self.__token = session_token
        self.driver.execute_cdp_cmd(
            'Network.setCookie',
            {
                'domain': 'chat.openai.com',
                'path': '/',
                'name': '__Secure-next-auth.session-token',
                'value': self.__token,
                'httpOnly': True,
                'secure': True,
            },
        )
        
    @staticmethod
    def get_xpath(element: WebElement):
        xpath = element.tag_name
        while element.tag_name != "html":
            element = element.find_element(By.XPATH, "..")
            neighbours = element.find_elements(By.XPATH, "../" + element.tag_name)
            level = element.tag_name
            if len(neighbours) > 1:
                level += "[" + str(neighbours.index(element) + 1) + "]"
            xpath = level + "/" + xpath
        return "//" + xpath