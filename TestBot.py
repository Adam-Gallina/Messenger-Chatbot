from Driver import Driver
from UserPrefs import UserPrefs
from MessengerCommands import MessengerCommands, SUCCESS_MSG, NOT_A_COMMAND_MSG
from CommandCall import CommandCall

#Additional bot commands
from BasicBotCommands import GetBasicCommands
from FunCommands import GetFunCommands
from CopyPaste import GetCopyPaste
from TicTacToe import GetTicTacToe
from BwudaBot import GetBwudaBot

#Messenger Chatbot | created by Adam Gallina | V1.1
#
# Dependencies:
# -Selenium (pip install selenium)
# -Google Chrome (https://www.google.com/chrome/?brand=CHBD&gclid=Cj0KCQjws_r0BRCwARIsAMxfDRiLVMWtfqG-iWJh6ILGHWEETOU_8jKHH0uwJDXCwcbjJvuUNcyRfDwaApOPEALw_wcB&gclsrc=aw.ds)
# -Chromedriver (https://chromedriver.chromium.org/downloads)
# -Datetime (pip install datetime)
#
#
# An example Bot using the Driver, UserPrefs, and MessengerCommands files
# The current build will only look at the most recent message, which can be potentially covered up by other messages
#
# !!! Make sure to change d = Driver("username", "password") to the username and password tied to the Facebook Messenger account you want to run the bot on
#
#############################################################################################################
## Command Form: @hh.mm !command_name #target_chat : arg1 ~ arg2 ~ ... ~ argN                              ##
##                - @hh.mm: (optional) Specifies a time for the command to be processed                    ##
##                - !command_name: (required) The name of the command to use                               ##
##                - #target_chat: (optional) Choose to send the output of the command to a different chat  ##
##                - arg1 ~ arg2 ~ ... ~ argN: (command-specific) arguments to send to the command          ##
#############################################################################################################



#Gives the user the ability to close the bot on Messenger
### Command: !exit
### Args[0]
running = True
def CloseBot(driver, args, chathead):
    global running
    running = False
    driver.SendText('Goodbye')
    return SUCCESS_MSG

username = "your email here"
password = "your password here"

#Create a custom Driver class and log it in to Messenger
d = Driver(username, password)

#Create a new UserPrefs class with the Chathead Ids taken from the Messenger page (logging in will automatically suspend the program until the page loads)
#Sometimes the chat area won't load with the page, and the program will error out here. I haven't figured out a good way to check for whether or not the chat area has loaded yet
#Gives UserPrefs the username to make account-specific UserPref files
prefs = UserPrefs(d.GetChatheadIds(), username)


#Put the bot on the chat you want it to consider the main chat
baseChat = prefs.GetChatID(prefs.GetUserSetting('basechat'))
if baseChat == 'Not found':
    print(f'Invalid basechat name {prefs.GetUserSetting("basechat")}')
    d.Close()
    quit()
d.SetMasterChat(baseChat)
d.ReturnToMasterChat()

#Set up commands
mc = MessengerCommands([CommandCall('exit', CloseBot, 8)] #Add command stored within this file
                       + GetFunCommands() #Add commands stored in another file
                       + GetBasicCommands(prefs)
                       + GetCopyPaste()
                       + GetTicTacToe(prefs)
                       + GetBwudaBot(), 'basic bot')

#Run until CloseBot() is called in Messenger
while running:
    if d.CheckSlowDownNotification():
        print('Slow down warning has appeared')
        d.ConfirmSlowDownNotification()

    #Check every chat on the page
    for chatName in prefs.GetChatNames():
        chatId = prefs.GetChatID(chatName)
        #Check if a given chat has a notification icon with it (if true, there are new messages to read)
        if d.CheckChatNotification(chatId) or d.currChatId == chatId:
            #Get the messages in the chat
            msgs = d.GetMessages(chatId)

            result = ''
            if len(msgs) > 0:
                #Check if the most recent message is a command/run it if it is
                result = mc.CheckMessage(d, prefs.GetChatID, prefs.GetChathead(chatName), msgs[-1])

            #Send a message to the chat if the result of the command was not expected
            if not result == SUCCESS_MSG and not result == NOT_A_COMMAND_MSG:
                d.SendText(result)
        #Check all queued messages (messages with a time specified)
        mc.RunQueue()

#Shut down the chatbot
d.Close()
