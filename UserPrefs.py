from os import path

class UserPrefs:
    varDivider = '~'
    fileDivider = '=====\n'

    chatHeads = {}

    settings = {}

    #Call functions to load the UserPrefs file and create Chathead profiles
    #Input: {String name : String chatID} chatIds, String username
    def __init__(self, chatIds, username):
        #print('Chat IDs are', len(chatIds))
        #print(chatIds)
        if '@' in username:
            username = username.split('@')[0]
        self.username = username
        if path.isfile('User Prefs ' + username):
            try:
                self.GetUserPrefs(chatIds, username)
            except: #In case something goes wrong while opening the file - it got modified externally, etc
                print('Something went wrong while reading the UserPrefs file, do you want to format the file with default values?')
                if input('y/n > ').lower() == 'y':
                    print('Creating new UserPrefs...')
                    self.CreateUserPrefs(chatIds, username)

        else:
            print('No UserPrefs found, generating new UserPrefs with chatIds')
            self.CreateUserPrefs(chatIds, username)

    #Create a UserPrefs file if none exist and assign it default values
    #Input: {String name : String chatID} chatIds, String username
    def CreateUserPrefs(self, chatIds, username):
        with open('User Prefs ' + username, 'w') as f:
            for key in chatIds.keys():
                f.write(f'{key}{self.varDivider}{key}{self.varDivider}0\n')
                self.chatHeads.update({ key:Chathead(key, chatIds[key], 0)})
            f.write(self.fileDivider)
            f.write(f'basechat={list(self.chatHeads.keys())[0]}\n')
            self.settings.update({'basechat': list(self.chatHeads.keys())[0]})

    #Open the UserPrefs file, and send the sections to their specific functions
    #Input: {String name : String chatID} chatId, String username
    def GetUserPrefs(self, chatIds, username):
        with open('User Prefs ' + username, 'r') as f:
            lines = f.read().split(self.fileDivider)
            self.GetNicknames(lines[0].split('\n')[:-1], chatIds)
            self.UpdateNicknames(chatIds)
            self.GetUserSettings(lines[1].split('\n')[:-1])

    #Split the top half of the file into names and accessLevels, and create chatHead [] with their data
    #Input: [string] fileData, {String name : String chatID} chatId
    def GetNicknames(self, fileData, chatIds):
        for line in fileData:
            prefs = line.split(self.varDivider)

            name = prefs[0]
            nickname = prefs[1]
            access = int(prefs[2])

            if not chatIds.get(name):
                continue

            self.chatHeads.update({ nickname:Chathead(name, chatIds.get(name), access) })
            chatIds.pop(name)

    #Check to see if the bot found any new chatheads that weren't already saved to the file, and create data for them
    #Input: {String name : String chatID} chatId
    def UpdateNicknames(self, chatIds):
        if len(chatIds) == 0:
            return
        for i in chatIds.keys():
            self.chatHeads.update({ i:Chathead(i, chatIds.get(i), 0) })
        self.SetUserPrefs()

    #Gets user settings from the second half of the file data
    # Input: String fileData
    def GetUserSettings(self, fileData):
        for line in fileData:
            newSetting = line.split('=')
            self.settings.update({newSetting[0]: newSetting[1]})

    #Save the current UserPrefs (rewrite the file)
    def SetUserPrefs(self):
        if len(self.chatHeads) == 0:
            print('Tried to save null user prefs, call GetUserPrefs() first')
            return

        with open('User Prefs ' + self.username, 'w') as f:
            for key in self.chatHeads.keys():# if len(self.chatNicknames) != 0 else self.chatIds.keys():
                f.write(f'{self.chatHeads[key].name}{self.varDivider}{key}{self.varDivider}{self.chatHeads[key].accessLevel}\n')
            f.write(self.fileDivider)
            for key in self.settings.keys():
                print(f'{key}={self.settings[key]}')
                f.write(f'{key}={self.settings[key]}\n')

    #Change the nickname of a chathead
    #Input: String name, String nickname
    #Output: bool result
    def ChangeNickname(self, name, nickname):
        if not self.chatHeads.get(name):
            return False

        if name == self.GetUserSetting('basechat'):
            self.ChangeUserSetting('basechat', nickname)

        self.chatHeads.update({ nickname:self.chatHeads.get(name) })
        self.chatHeads.pop(name)

        self.SetUserPrefs()
        return True

    #Change the access level of a chathead
    #Input: String name, int newLevel
    #Output: bool result
    def ChangeAccessLevel(self, name, newLevel):
        if not self.chatHeads.get(name):
            return False
        if not type(newLevel) == int:
            return False

        self.chatHeads.get(name).accessLevel = newLevel
        self.SetUserPrefs()
        return True

    #Returns the id associated with a given name, or a default value if it doesn't exist
    #Input: String chatName
    #Output: String chatId
    def GetChatID(self, chatName):
        if not self.chatHeads.get(chatName):
            return "Not found"
        return self.chatHeads.get(chatName).chatId

    #Use the name stored in a Chathead object to get an ID
    #Input: String realName
    #Output: String chatId
    def GetChatIDwithRealName(self, realName):
        for i in self.chatHeads.keys():
            if self.chatHeads[i].name == realName:
                return self.chatHeads[i].chatId
        return "Not found"

    #Get a list of every chatId in the current chatheads - used to iterate through/open every chat
    #Output: String[] chatIds
    def GetAllChatIds(self):
        ids = []
        for i in self.chatHeads.keys():
            ids.append(self.chatHeads[i].chatId)
        return ids

    #Get a list of every chat nickname in the current chatheads
    #Output: String[] chatNames
    def GetChatNames(self):
        names = []
        for i in self.chatHeads.keys():
            names.append(i)
        return names

    #Get the access level of a given chat head, or a default value if it doesn't exist
    #Input: String chatName
    #Output: int accessLevel
    def GetAccessLevel(self, chatName):
        if not self.chatHeads.get(chatName):
            return 0
        return self.chatHeads.get(chatName).accessLevel

    #Return the chathead object associated with a specific name
    #Input: String chatName
    #Output: Chathead chathead
    def GetChathead(self, chatName):
        return self.chatHeads.get(chatName, Chathead('Not found', 'Not found', 0))

    #Returns the setting value of a given setting (or a default value if not found)
    #Input: String settingName
    #Output: String settingValue
    def GetUserSetting(self, settingName):
        return self.settings.get(settingName, 'Setting not found')

    #Change the value held by a setting
    #Input: String settingName, String newValue
    #Output: bool result
    def ChangeUserSetting(self, settingName, newValue):
        if not self.settings.get(settingName):
            #print(f'Setting {settingName} does not exist')
            return False
        self.settings[settingName] = newValue
        self.SetUserPrefs()
        return True
    #endregion

#Stores the data needed by each chathead
class Chathead:
    def __init__(self, name, chatId, accessLevel):
        self.name = name
        self.chatId = chatId
        self.accessLevel = accessLevel