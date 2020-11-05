import time

from StringHandling import *

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Driver:
    #URLs
    messengerUrl = "http://messenger.com"
    #HTML prefix/suffixes
    namePrefix = "data-tooltip-content=\""
    idPrefix = "_1ht5\" id=\"js_"
    #chatSenderPrefix = "h5 aria-label=\""
    #chatSenderSuffix = ""
    #chatPrefix = "tabindex=\"0\" aria-label=\""
    chatPrefix = "<span class=\"_3oh- _58nk\">"
    chatSuffix = "</span>"
    #HTML elements
    inputBox = "_5rp8"
    messageArea = "_4_j4"
    chatheadArea = "uiScrollableAreaContent"
    #Slow down warning elements
    warningBoxClass = '_4t2a'
    warningBoxConfirm = 'layerConfirm'

    driver = ''
    masterChatId = ''
    baseChatId = ''
    currChatId = ''

    counter = 0

    #Create a driver by calling Login
    def __init__(self, username, password):
        self.driver = self.Login(username, password)

    #Open Facebook Messenger in Google Chrome and logs in with a given Username/Password
    #Input: String username, String password
    #Output: Driver driver
    def Login(self, username, password):
        newDriver = webdriver.Chrome()
        newDriver.get(self.messengerUrl)

        WebDriverWait(newDriver, 20).until(EC.presence_of_element_located((By.ID, "email")))
        time.sleep(1)
        newDriver.find_element(By.ID, "email").send_keys(username)
        newDriver.find_element(By.ID, "pass").send_keys(password)
        newDriver.find_element(By.ID, "loginbutton").click()

        return newDriver

    #Iterates through the InnerHTML to get every name and html ID corresponding to the loaded chatheads
    #Input: none
    #Output: Dictionary { String name: String ID }
    def GetChatheadIds(self):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, self.chatheadArea)))
        time.sleep(1)

        newIds = {}

        chatHeadData = self.driver.find_element(By.CLASS_NAME, self.chatheadArea).get_attribute("innerHTML").encode('unicode-escape').decode('utf-8')
        length = len(chatHeadData)

        lastId = ""
        for c in range(length):
            if length - c < len(self.namePrefix):
                break

            if chatHeadData[c] == self.idPrefix[0] and chatHeadData[c:c + len(self.idPrefix)] == self.idPrefix:
                if not lastId == '':
                    print(f'Overwriting unused ID when setting IDs: {lastId}')
                lastId = chatHeadData[c + 11:c + len(self.idPrefix) + 1]
            elif chatHeadData[c] == self.namePrefix[0] and chatHeadData[c:c + len(self.namePrefix)] == self.namePrefix:
                name = ClipStringFromStart(chatHeadData[c + len(self.namePrefix):], '"')
                if not name == '':
                    if lastId == '':
                        print(f'Tring to use a null ID for {name}')
                        continue
                    newIds.update({ name:lastId })
                    lastId = ''
                    continue

        return newIds

    #Sends a string to the currently active textbox on Messenger
    #Input: String message
    def SendText(self, message):
        textbox = self.driver.find_element(By.CLASS_NAME, self.inputBox)

        ActionChains(self.driver).move_to_element(textbox).click().send_keys(message + Keys.RETURN).perform()

    # Change to a chat without changing the base chat
    #Input String chatId
    def ChangeToChat(self, chatId):
        ActionChains(self.driver).move_to_element(self.driver.find_element(By.ID, chatId)).click().perform()
        self.currChatId = chatId

    #Change the last chat that sent a command
    #Input: String chatID (UserPrefs.GetChatId(chatName)
    def ChangeBaseChat(self, chatId):
        self.baseChatId = chatId
        #ActionChains(self.driver).move_to_element(self.driver.find_element(By.ID, self.baseChatId)).click().perform()

    #Return to base chat
    def ReturnToBaseChat(self):
        self.ChangeToChat(self.baseChatId)

    #Change the main chat of the bot
    #Input: String ChatID (UserPrefs.GetChatId(chatName))
    def SetMasterChat(self, chatId):
        self.masterChatId = chatId

    #Return to master chat
    def ReturnToMasterChat(self):
        self.ChangeToChat(self.masterChatId)

    #Checks the HTML of a given ID to see if it contains a notification dot
    #Input: String chatID (UserPrefs.GetChatId(chatName)
    #Output: boolean notification
    #def CheckNotification(self, chatId):
    #    return self.driver.find_element(By.ID, chatId).find_element(By.XPATH, '..').find_element(By.XPATH, '.// div [2] / div / div[2]').get_attribute('class').equals('_6zv_')

    #Opens a specific chat and iterates through the HTML to find all of the loaded messages in the chat
    #Input: String chatId
    #Output: String[] chatMessages
    def GetMessages(self, chatId):
        self.ChangeToChat(chatId)
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, self.messageArea)))
        time.sleep(1)

        chatData = self.driver.find_element(By.CLASS_NAME, self.messageArea).get_attribute('innerHTML')
        currMessages = []
        currName = ''
        for c in range(len(chatData)):
            if len(chatData) - c < len(self.chatPrefix):#len(self.chatSenderPrefix):
                break

            #if chatData[c] == self.chatSenderPrefix[0] and chatData[c:c + len(self.chatSenderPrefix)] == self.chatSenderPrefix:
            #    currName = ClipStringFromStart(chatData[c + len(self.chatSenderPrefix):], self.chatSenderSuffix)

            if chatData[c] == self.chatPrefix[0] and chatData[c:c + len(self.chatPrefix)] == self.chatPrefix:
                newMessage = ClipStringFromStart(chatData[c + len(self.chatPrefix):], self.chatSuffix)
                currMessages.append(newMessage)

        return currMessages

    # Checks the HTML of a given ID to see if it contains a notification dot
    # Input: String chatID (UserPrefs.GetChatId(chatName)
    # Output: boolean notification
    def CheckChatNotification(self, chatId):
        try:
            return self.driver.find_element_by_id(chatId).find_element_by_xpath('..').find_element_by_xpath('.// div [2] / div / div[2]').get_attribute("class") == '_6zv_'
        except StaleElementReferenceException:
            return False

    #Checks if the webpage is showing a slow down notification because too many messages have been sent...lol
    #Output: boolean result
    def CheckSlowDownNotification(self):
        return self.driver.find_elements_by_class_name(self.warningBoxClass)

    #Press the confirm button on the slow down notification
    #NOTE be careful to not send too many messages afterwards
    def ConfirmSlowDownNotification(self):
        self.driver.find_element_by_class_name(self.warningBoxConfirm).click()

    #Shuts down the driver and nulls its variable
    def Close(self):
        self.driver.close()
        self.driver = ''