from CommandCall import CommandCall
from MessengerCommands import SUCCESS_MSG
from UserPrefs import  Chathead
from Driver import Driver
from StringHandling import CheckArgLength, CheckArgType
import hashlib
names = { 'ian':97, 'hoher piest':97, 'hoher priest':97, 'daniel':100, 'bwuda':100, 'keeton':4 }

#Creates a hash code from a string
#Input: string name
#Output: int hash
def GetHash(name):
    return int(hashlib.sha256(name.lower().encode('utf-8')).hexdigest(), 16) % 1000

#Calculates how much bwuda wuvs you from a hash code
### Args[1]: String name
def CheckBwudaWuv(driver, args, chatHead):
    if not CheckArgLength(args, 1):
        return f'Not enough arguments, use the format !CheckWuv : name'

    name = args[0].lower()
    bwudaName = 'bwuda'

    hash1 = GetHash(name)
    hash2 = GetHash(bwudaName) * 10
    result = int(min(hash1, hash2) / max(hash1, hash2) * 100)

    result = names[name] if name in names else result

    if result > 100:
        result -= 100
    driver.SendText(f'Bwuda wuvs you wif {result}% of his hed smackin powew')
    if result > 80:
        driver.SendText('Yo hed mus be as stwong as andwew\'s wif dat much hed smack powew')
    elif result < 20:
        driver.SendText('Oh dwat, u mus be a twenty suppowtew')

    return SUCCESS_MSG

#Gets bwuda bot commands
def GetBwudaBot():
    return [CommandCall('checkwuv', CheckBwudaWuv, 0)]