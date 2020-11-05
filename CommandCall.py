from UserPrefs import Chathead

class CommandCall:
    name = ''
    command = None
    accessLevel = 0

    def __init__(self, name, command, accessLevel = 0, ignoreSuspension = False):
        self.name = name
        self.command = command
        self.accessLevel = accessLevel
        self.ignoreSuspension = ignoreSuspension

    #Calls the command linked to the object
    #Input: String[] arguments
    #Output: The result of the called command
    def Call(self, driver, arguments, chathead):
        return self.command(driver, arguments, chathead)

    #Returns True/False if the input accessLevel is at least the access level of the command
    #Input: int accessLevel
    #Output: Bool result
    def CheckAccessLevel(self, clientAccessLevel):
        return clientAccessLevel >= self.accessLevel