from StringHandling import *
from CommandCall import CommandCall
from UserPrefs import Chathead

from datetime import datetime

# MessengerCommands - an object containing various functions to iterate through strings and determine whether or not that string is a command, and run those commands

SUCCESS_MSG = 'Success'
NOT_A_COMMAND_MSG = 'Not a command'

#Returns the current time in the form hh:mm
#### NOTE ####: Uses army time, and always has two digits in the minutes
#Output: String time
def GetCurrTime():
    currTime = datetime.now().time()

    h = currTime.hour
    m = currTime.minute

    m = str(m) if len(str(m)) == 2 else '0' + str(m)

    return f'{h}:{m}'

#Sends a message to the driver
### args[1]: The message you want to send
def SendMessage(driver, args, chathead):
    message = ''
    for i in args:
        message = i + ', '
    driver.SendText(message[:-2])
    return SUCCESS_MSG

class MessengerCommands:
    commandPrefix = '!'
    commandMid = ': '
    commandArgsSplitter = ' ~ '

    queuePrefix = '@'
    changeChatPrefix = '#'

    commands = {}
    commandQueue = {}

    #Create a a new MessengerCommands object with potential additional commands
    #Input: Array[CommandCall] customCommands
    def __init__(self, customCommands = [], suspendMessage = ''):
        for cmd in customCommands:
            self.commands.update({ cmd.name:cmd })

        self.commands.update({ 'send' : CommandCall('send', SendMessage),
                               'checkqueue' : CommandCall('checkqueue', self.CheckQueue),
                               'suspend' : CommandCall('suspend', self.SuspendBot, 9, True),
                               'checksuspend' : CommandCall('checksuspend', self.CheckSuspension, 0, True)})

        self.suspendMessage = suspendMessage
        self.suspended = False

    #Checks a message to see if it is a valid command, attempts to call that command
    #Input: Driver driver, UserPrefs.GetChatId idCheck, Chathead chathead, String message
    #Output: String result
    def CheckMessage(self, driver, idCheck, chathead, message):
        if not message[0] in [self.commandPrefix, self.queuePrefix]:
            return NOT_A_COMMAND_MSG

        print(f'{chathead.name}) {message}')
        if not ':' in message:
            message += ' '

        cmd = message.split(self.commandMid)
        commandName = ClipString(cmd[0], self.commandPrefix, ' ', True)
        time = ClipString(cmd[0], self.queuePrefix, ' ', True)
        targetChat = ClipString(cmd[0], self.changeChatPrefix, '', True)
        args = cmd[1].split(self.commandArgsSplitter) if len(cmd) == 2 else []
        for i in range(len(args)):
            args[i] = args[i].strip()

        targetChatId = ''
        if not targetChat == '':
            targetChatId = idCheck(targetChat)
            if targetChatId == 'Not found':
                return f'Invalid chat name {targetChat}'
            #driver.ChangeBaseChat(targetChatId)

        if not time == '': #Queue the command
            if CheckTimeFormat(time):
                return self.QueueCommand(driver, time, targetChatId, commandName, args, chathead)
            else:
                return f'Invalid time format: {time} (Use HH:MM, zeroes are necessary)'
        else: #Do the command
            return self.CallCommand(driver, targetChatId, commandName, args, chathead)

    #Calls a command
    #Input: Driver driver, String targetChatId, String commandName, Chathead chathead
    #Output: String result
    def CallCommand(self, driver, targetChatId, commandName, args, chathead):
        if self.commands.get(commandName.lower()):
            currCommand = self.commands[commandName.lower()]
            if not currCommand.CheckAccessLevel(chathead.accessLevel):
                return 'Sorry, you can\'t use that command'

            if self.suspended and not currCommand.ignoreSuspension:
                return ''

            driver.ChangeBaseChat(driver.currChatId)
            changedChat = False
            if not targetChatId == '':
                driver.ChangeToChat(targetChatId)
                changedChat = True

            result = currCommand.Call(driver, args, chathead)

            if changedChat:
                driver.ReturnToBaseChat()
                if result == 'Success':
                    return 'Chat sent successfully'
            return result
        else:
            return f'Invalid command: {commandName}'

    #Adds a command to the queue, to be processed at the time specified by the command
    #Input: Driver driver, String time, String targetChatId, String commandName, String[] args, Chathead chathead
    def QueueCommand(self, driver, time, targetChatId, commandName, args, chathead):
        if self.commandQueue.get(time):
            self.commandQueue[time].append([driver, targetChatId, commandName, args, chathead])
        else:
            self.commandQueue.update({time: [[driver, targetChatId, commandName, args, chathead]]})
        return 'Command Queued'

    #Iterates through the command queue and calls any commands that match the current time from GetCurrTime()
    def RunQueue(self):
        currTime = GetCurrTime()
        newQueue = self.commandQueue.copy()

        for time in self.commandQueue.keys():
            if time == currTime or time.lower() == 'now':
                for command in self.commandQueue[time]:
                    self.CallCommand(command[0], command[1], command[2], command[3], command[4])
                newQueue.pop(time)

        self.commandQueue = newQueue

    #Prints every message and the time to send it currently in the queue
    ### Args[0]
    def CheckQueue(self, driver, args, chathead):
        if len(self.commandQueue) == 0:
            driver.SendText('No messages in queue right now')
            return 'Success'

        #print(self.commandQueue)
        for key in self.commandQueue.keys():
            for command in self.commandQueue[key]:
                #print(f'{key}: !{command[2]} : {command[3]}' + (', target chat: ' + command[1]) if not command[1] == '' else '')
                driver.SendText(f'{key}: !{command[2]} : {command[3]}' + (', target chat: ' + command[1]) if not command[1] == '' else '')
        return 'Success'

    #Toggles whether or not most commands can run
    ### Args[1]: string botName
    def SuspendBot(self, driver, args, chathead):
        if self.suspendMessage == '':
            return 'Bot cannot be suspended - no suspendMessage set'

        if not CheckArgLength(args, 1):
            return 'Wrong number of arguments, use the form !suspend : bot_code'

        if not self.suspendMessage == args[0]:
            return SUCCESS_MSG

        self.suspended = not self.suspended
        driver.SendText(f'Bot "{self.suspendMessage}" suspended' if self.suspended else f'Bot "{self.suspendMessage}" unsuspended')
        return SUCCESS_MSG

    #Check if a specific bot is suspended
    ### Args[1]: String botName
    def CheckSuspension(self, driver, args, chathead):
        if self.suspendMessage == '':
            return 'Bot cannot be suspended - no suspendMessage set'

        if not CheckArgLength(args, 1):
            return 'Wrong number of arguments, use the form !checksuspend : bot_code'

        if not self.suspendMessage == args[0]:
            return SUCCESS_MSG

        driver.SendText(f'{self.suspendMessage} is {"suspended" if self.suspended else "not suspended" }')
        return SUCCESS_MSG
