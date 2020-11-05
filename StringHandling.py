#Input: String string, String startPhrase, String endPhrase
#Output: String result
def ClipString(string, startPhrase, endPhrase, removeWhitespace=False):
    ret = ''
    for i in range(len(string)):
        if string[i] == startPhrase[0] and string[i:i + len(startPhrase)] == startPhrase:
            if endPhrase == '':
                ret = string[i + len(startPhrase):]
                break
            return ClipStringFromStart(string[i + len(startPhrase):], endPhrase, removeWhitespace)
    if removeWhitespace:
        ret = ret.strip()
    return ret

#Input: String string, String endPhrase
#Output: String result
def ClipStringFromStart(string, endPhrase, removeWhitespace=False):
    ret = ''
    for i in range(len(string)):
        if string[i] == endPhrase[0]:
            if len(endPhrase) > 1 and string[i:i + len(endPhrase)] == endPhrase:
                ret = string[:i]
                break
            elif len(endPhrase) == 1:
                ret = string[:i]
                break
    if removeWhitespace:
        ret = ret.strip()
    return ret

#Input: String time (HH.MM)
#Output: Bool result
def CheckTimeFormat(string):
    if string.lower() == 'now':
        return True

    string = string.split(':')
    try:
        int(string[0])
        int(string[1])
    except ValueError:
        return False
    return len(string[0]) == 2 and len(string[1]) == 2

#Input: String[] args, int/int[] requiredLength
#Output: bool result
def CheckArgLength(args, requiredLength):
    if type(requiredLength) == int:
        return len(args) == requiredLength
    return len(args) in requiredLength

#Input: Type argType, String arg
#Output: bool result
def CheckArgType(argType, arg):
    try:
        argType(arg)
    except TypeError:
        return False
    return True