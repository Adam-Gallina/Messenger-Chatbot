from CommandCall import CommandCall
from MessengerCommands import SUCCESS_MSG

#FunCommands: Random functions that are more or less pointless except for causing pain

#Facebook warns you and potentially blocks you if you send too many messages...this caps the maximum spammed messages per command
SPAM_MAX = 75

#Spam a target chat :) I recommend you don't use this without a target chat
### Command: !spam
### Args[2]: message_to_send ~ number_of_messages
def Spam(driver, args, chathead):
    if len(args) == 1:
        return 'Too few arguments - Use the format !spam #target : message ~ [number of messages]'
    if len(args) > 2:
        return 'Too many arguments - Use the format !spam #target : message ~ number of messages'

    numbMsgs = 0
    try:
        numbMsgs = int(args[1])
        if numbMsgs < 1:
            raise ValueError
    except ValueError:
        return f'{args[1]} is not a valid number'

    if numbMsgs > SPAM_MAX:
        return f'{numbMsgs} is too large, use a number smaller than {SPAM_MAX}'

    for i in range(numbMsgs):
        if driver.CheckSlowDownNotification():
            driver.ConfirmSlowDownNotification()
            return 'Ended early, too many messages sent'

        driver.SendText(args[0])
    return SUCCESS_MSG

#Return the CommandCall of all functions within FunCommands
def GetFunCommands():
    return [CommandCall('spam', Spam, 3)]