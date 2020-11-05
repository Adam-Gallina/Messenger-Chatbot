from CommandCall import CommandCall
from MessengerCommands import SUCCESS_MSG
from UserPrefs import  Chathead
from Driver import Driver
from StringHandling import CheckArgLength, CheckArgType
import random

def Copy(driver, args, chathead):
    if not CheckArgLength(args, 1):
        return 'Wrong number of arguments, use the form !Copy : message'

    with open(chathead.name + '-pastes', 'a') as f:
        f.write('\n' + args[0])

    driver.SendText('Copied')
    return SUCCESS_MSG

def Paste(driver, args, chathead):
    index = -1
    if CheckArgLength(args, 1):
        if not CheckArgType(int, args[0]):
            return f'{args[0]} is not a valid integer'
        index = int(args[0]) - 1
        if index < 0:
            index += 1

    with open(chathead.name + '-pastes', 'r') as f:
        lines = f.readlines()

        if len(lines) == 0:
            driver.SendText("No pastes yet - use !Copy : copy_message to create one!")
            return SUCCESS_MSG

        if len(lines) < abs(index):
            return f'Only {len(lines)} copies available - {index} is too big'

        driver.SendText(lines[index])
        return SUCCESS_MSG

def PasteAll(driver, args, chathead):
    startIndex = 0
    if CheckArgLength(args, 1):
        if not CheckArgType(int, args[0]):
            return f'{args[0]} is not a valid integer'
        startIndex = int(args[0]) - 1
        if startIndex < 0:
            startIndex += 1

    with open(chathead.name + '-pastes', 'r') as f:
        lines = f.readlines()

        if len(lines) == 0:
            driver.SendText("No pastes yet - use !Copy : copy_message to create one!")
            return SUCCESS_MSG

        if startIndex < 0:
            startIndex = len(lines) + startIndex

        for i in range(startIndex, len(lines)):
            if lines[i] == '\n':
                continue
            driver.SendText(f'{i + 1}: {lines[i]}')

        return SUCCESS_MSG

def PasteRandom(driver, args, chatHead):
    with open(chatHead.name + '-pastes', 'r') as f:
        lines = f.readlines()
        driver.SendText(lines[random.randint(0, len(lines) - 1)])
    return SUCCESS_MSG

def DeletePaste(driver, args, chatHead):
    index = -1
    if CheckArgLength(args, 1):
        if not CheckArgType(int, args[0]):
            return f'{args[0]} is not a valid integer'
        index = int(args[0]) - 1
        if index < 0:
            index += 1
    lines = []

    with open(chatHead.name + '-pastes', 'r') as f:
        lines = f.readlines()

    if len(lines) < abs(index):
        return f'Only {len(lines)} copies available - {index} is too big'
    removed = lines.pop(index)

    with open(chatHead.name + '-pastes', 'w') as f:
        f.writelines(lines)

    driver.SendText(f'Removed: {removed}')
    return SUCCESS_MSG

def GetCopyPaste():
    return [CommandCall('copy', Copy, 1),
            CommandCall('paste', Paste, 1),
            CommandCall('pasteall', PasteAll, 1),
            CommandCall('pasterandom', PasteRandom, 1),
            CommandCall('deletepaste', DeletePaste, 1)]