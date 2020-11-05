from CommandCall import CommandCall
from MessengerCommands import GetCurrTime, SUCCESS_MSG
from StringHandling import CheckArgLength
from UserPrefs import Chathead

#BasicBotCommads - contains helper functions to modify the UserPrefs file through Messenger

userPrefs = ''

#Returns the current time according to MessengerCommands.GetCurrTime()
### Args[0]
def CheckCurrTime(driver, args, chathead):
    driver.SendText(f'The time is {GetCurrTime()}')
    return SUCCESS_MSG

#Sends every chat nickname to the driver
### Args[0]
def CheckChatNames(driver, args, chathead):
    driver.SendText('Printing all Chat names')
    for i in userPrefs.GetChatNames():
        driver.SendText(f'- {i}')
    return SUCCESS_MSG

#Changes a chat name on UserPrefs
### Args[2]: current_name ~ new_name
def ChangeChatName(driver, args, chathead):
    if len(args) == 1:
        return 'Too few arguments - Use the format !setname : target chat name ~ new chat name'
    if len(args) > 2:
        return 'Too many arguments - Use the format !setname : target chat name ~ new chat names'

    if not userPrefs.ChangeNickname(args[0], args[1]):
        return f'Chat "{args[0]}" does not exist'
    driver.SendText(f'{args[0]} changed successfully to {args[1]}!')
    return SUCCESS_MSG

#Change the access level of a chat
### args[2]: target_chat_name ~ new_access_level
def ChangeAccessLevel(driver, args, chathead):
    if not CheckArgLength(args, 2):
        return 'Wrong number of arguments, use the form !changeaccess : target_chat_name ~ new_access_level'

    try:
        accessLevel = int(args[1])
    except ValueError:
        return 'Please enter an integer access level'

    if not userPrefs.ChangeAccessLevel(args[0], accessLevel):
        return f'Chat "{args[0]}" does not exist'
    driver.SendText(f'{args[0]}\'s access level has been updated to {args[1]}!')
    return SUCCESS_MSG

#Function to get all commands stored in BasicBotCommands
#Input: UserPrefs prefs - The user settings created in the main bot file
def GetBasicCommands(newPrefs):
    global userPrefs
    userPrefs = newPrefs

    return [CommandCall('checktime', CheckCurrTime),
            CommandCall('getnames', CheckChatNames),
            CommandCall('changename', ChangeChatName, 8),
            CommandCall('changeaccess', ChangeAccessLevel, 10)]