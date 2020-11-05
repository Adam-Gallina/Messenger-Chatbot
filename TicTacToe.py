from CommandCall import CommandCall
from MessengerCommands import SUCCESS_MSG
from UserPrefs import  Chathead
from Driver import Driver
from StringHandling import CheckArgLength, CheckArgType
import random

NO_GAMES = 'No games'
GAME_OVER = 'Game over'

prefs = ''

games = []

#Gets a Game object from the list if it exists
#Input: string name
#Output: Game game
def GetGame(name):
    for i in games:
        if i.Participating(name):
            return i
    return NO_GAMES

#Removes a Game object from the list if it exists
#Input: string name
#Output: string result
def RemoveGame(name):
    for i in range(len(games)):
        if games[i].Participating(name):
            games.pop(i)
            return SUCCESS_MSG
    return NO_GAMES


#Create a new game and send a challenge to the opponent if the user doesn't have any active games
### args[2]: string opponentName, string symbol
def NewGame(driver, args, chatHead):
    if not CheckArgLength(args, [1, 2]):
        return f'Wrong number of arguments, use the form !newttt : target_chat ~ symbol'

    if not GetGame(chatHead.name) == NO_GAMES:
        return f'You already have a game created - use !showttt to see it'

    symbol = 'X'
    if len(args) == 2:
        symbol = args[1]

    opponent = prefs.GetChathead(args[0])
    if opponent.name == "Not found":
        return f'Invalid target_chat: {args[0]}'

    games.append(TTTgame(driver, chatHead.name, opponent.name, symbol))
    driver.ChangeToChat(prefs.GetChatIDwithRealName(opponent.name))
    driver.SendText(f'{chatHead.name} is challenging you to a game of Tic-Tac-Toe! Respond with "!jointtt : yes/no ~ symbol" to join!')
    driver.ReturnToBaseChat()
    driver.SendText(f'Challenge sent to {args[0]}!')
    return SUCCESS_MSG

#Accepts an existing challenge
### args[2]: string response, string symbol
def JoinGame(driver, args, chatHead):
    if not CheckArgLength(args, [1, 2]):
        return f'Wrong number of arguments, use the form !jointtt : yes/no ~ symbol to join'

    game = GetGame(chatHead.name)
    if game == NO_GAMES:
        return f'You do not have any active Tic-Tac-Toe games'

    if args[0].lower()[0] == 'n':
        driver.ChangeToChat(prefs.GetChatIDwithRealName(game.GetOpponent(chatHead.name)))
        driver.SendText(f'{chatHead.name} did not accept your Tic-Tac-Toe challenge :(')
        driver.ReturnToBaseChat()
        driver.SendText('Responded with no')
        RemoveGame(chatHead.name)
        return SUCCESS_MSG

    if CheckArgLength(args, 2):
        game.SetP2Symbol(args[1])

    driver.ChangeToChat(prefs.GetChatIDwithRealName(game.GetOpponent(chatHead.name)))
    driver.SendText(f'{chatHead.name} accepted your Tic-Tac-Toe challenge!')
    driver.ReturnToBaseChat()
    driver.SendText('Responded with yes!')

    game.StartGame()

    return SUCCESS_MSG

#Takes a turn in an existing game
### args[1] string position
def PlayGame(driver, args, chatHead):
    if not CheckArgLength(args, 1):
        return 'Wrong number of arguments, use the form !playttt : rowcolumn'

    game = GetGame(chatHead.name)

    if game == NO_GAMES:
        driver.SendText('You do not have an active Tic-Tac-Toe game')
        return SUCCESS_MSG

    if not len(args[0]) == 2:
        return f'{args[0]} is in an invalid format, use the format \'rowcolumn\' to pick a space - e.g. B2'

    row = args[0][0]
    col = args[0][1]

    result = game.TakeTurn(chatHead.name, row, col)
    if result == GAME_OVER:
        RemoveGame(chatHead.name)
        return SUCCESS_MSG
    return result

#No functionality yet
def NudgeGame(driver, args, chatHead):
    print()

#Prints the game board to the chat
### args[0]
def ShowGame(driver, args, chatHead):
    game = GetGame(chatHead)

    if game == NO_GAMES:
        driver.SendText('You do not have an active Tic-Tac-Toe game')
        return SUCCESS_MSG

    game.PrintBoard()
    driver.SendText(game.GetTurn(chatHead.name))
    return SUCCESS_MSG

#No functionality yet
def Help(driver, args, chatHead):
    print()

#Returns the tictactoe commands
def GetTicTacToe(userPrefs):
    global prefs
    prefs = userPrefs
    return [CommandCall('newttt', NewGame),
            CommandCall('jointtt', JoinGame),
            CommandCall('playttt', PlayGame),
            CommandCall('nudgettt', NudgeGame),
            CommandCall('showttt', ShowGame),
            CommandCall('helpttt', Help)]

class TTTgame:
    def __init__(self, driver, p1, p2, p1symbol):
        self.driver = driver
        self.p1 = p1
        self.p2 = p2
        self.p1symbol = p1symbol
        self.p2symbol = 'O' if not p1symbol == 'O' else 'X'
        self.currTurn = 1

        self.board = [['_', '_', '_'],
                 ['_', '_', '_'],
                 ['_', '_', '_']]

    #Changes player 2's symbol (p1's is set in __init__)
    def SetP2Symbol(self, symbol):
        self.p2symbol = symbol

    #Check if a name is playing this object's game
    #Input: string chatName
    #Output: bool result
    def Participating(self, name):
        return self.p1 == name or self.p2 == name

    #Returns the name of the opponent
    #Input: string chatName
    #Iutout: string opponentName
    def GetOpponent(self, name):
        return self.p1 if self.p2 == name else self.p2

    #Starts the game and prompts the first players turn
    def StartGame(self):
        self.currTurn = 1 if random.randint(0, 1) else -1
        self.PromptTurn()

    #Prompts a player for their turn
    def PromptTurn(self):
        global prefs
        self.driver.ChangeToChat(prefs.GetChatIDwithRealName(self.p1 if self.currTurn == 1 else self.p2))
        self.driver.SendText(f'It\'s your turn in your Tic-Tac-Toe game against {self.p2 if self.currTurn == 1 else self.p1}')
        self.PrintBoard()

    #Returns the whether or not it is a players turn
    #Input: string chatName
    #Output: string currTurn
    def GetTurn(self, playerName):
        return 'It is your turn' if playerName == (self.p1 if self.currTurn == 1 else self.p2) else 'It isn\'t your turn'

    #Prints the board to the driver at the current open chat
    def PrintBoard(self):
        b = self.board
        self.driver.SendText( '.____1_____2____3__')
        self.driver.SendText(f'A: .__{b[0][0]}__|__{b[0][1]}__|__{b[0][2]}__')
        self.driver.SendText(f'B: .__{b[1][0]}__|__{b[1][1]}__|__{b[1][2]}__')
        self.driver.SendText(f'C:     {"  " if b[2][0] == "_" else b[2][0] }    |    {"  " if b[2][1] == "_" else b[2][1]}    |    {"  " if b[2][2] == "_" else b[2][2]}  .')

    #Plays a turn if the playerName is correct
    #Input: String playerName, string row, string col
    def TakeTurn(self, playerName, row, col):
        if not playerName == (self.p1 if self.currTurn == 1 else self.p2):
            return 'Not your turn'

        if not row.lower() in ['a', 'b', 'c']:
            return f'{row} is an invalid row, use a, b, or c'
        if not col in ['1', '2', '3']:
            return f'{col} is an invalid column, use 1, 2, or 3'

        introw = ['a', 'b', 'c'].index(row.lower())
        intcol = int(col) - 1

        if not self.board[introw][intcol] == '_':
            return 'Can\'t play there'

        self.board[introw][intcol] = self.p1symbol if self.currTurn == 1 else self.p2symbol

        self.PrintBoard()

        endCheck = self.CheckWin()
        if endCheck == ' ':
            self.currTurn *= -1
            self.PromptTurn()
            return SUCCESS_MSG
        if endCheck == 'cg':
            self.driver.SendText('Cat\'s game, no winner :(')
            self.driver.ChangeToChat(prefs.GetChatIDwithRealName(self.GetOpponent(playerName)))
            self.driver.SendText('Cat\'s game, no winner :(')
            self.driver.ReturnToBaseChat()
            RemoveGame(playerName)
            return GAME_OVER
        else:
            self.driver.SendText('You win!')
            self.driver.ChangeToChat(prefs.GetChatIDwithRealName(self.GetOpponent(playerName)))
            self.PrintBoard()
            self.driver.SendText(f'{playerName} won Tic-Tac-Toe :(')
            self.driver.ReturnToBaseChat()
            RemoveGame(playerName)
            return GAME_OVER

    #Checks the board for win conditions or a cats game
    def CheckWin(self):
        cols = [[self.board[0][0], self.board[1][0], self.board[2][0]],
                [self.board[0][1], self.board[1][1], self.board[2][1]],
                [self.board[0][2], self.board[1][2], self.board[2][2]]]
        allFilled = True

        for row in self.board:
            if not '_' in row and row[0] == row[1] and row[0] == row[2]:
                return row[0]
            if row[0] == '_' or row[1] == '_' or row[2] == '_':
                allFilled = False

        for col in cols:
            if not '_' in col and col[0] == col[1] and col[0] == col[2]:
                return col[0]

        # Right oblique
        if not '_' in self.board[0][2] and self.board[0][2] == self.board[1][1] and self.board[0][2] == self.board[2][0]:
            return self.board[0][2]

        # Left oblique
        if not '_' == self.board[0][0] and self.board[0][0] == self.board[1][1] and self.board[0][0] == self.board[2][2]:
            return self.board[0][0]

        return 'cg' if allFilled else ' '