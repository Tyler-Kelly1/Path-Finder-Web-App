from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import asyncio

#python -m uvicorn backend.main:app --reload

def decodeColors(color):
    match(color):
        case 'rgb(211, 211, 211)':
            return '-'
        case 'rgb(165, 42, 42)':
            return 'X'
        case 'rgb(0, 96, 0)':
            return 'p'
        case 'rgb(255, 215, 0)':
            return 'G'

class Message(BaseModel):
    grid: List[List[str]]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

    
)

#GLOBAL Grid
global grid
grid = []

global active_connections



active_connections = {}

@app.post("/api/send")
async def receive_grid(message: Message):
    global grid
    grid = message.grid
    print(grid)
    return {"status": "Grid received", "grid": message.grid}


@app.websocket("/ws/{clientID}")
async def websocket_endpoint(websocket: WebSocket, clientID):
    global active_connections
    await websocket.accept()
    active_connections[clientID] = websocket


    try:
        while True:  # Keep connection alive
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket closed for: {e}")



@app.get("/api/getGrid/{clientID}")
async def send_grid(clientID):

    global active_connections
    global grid


   
    board = []
    indexR = 0

    websocket = active_connections[clientID]

    
    #Convert to game board
    for row in grid:

        board.append([])
        for color in row:
            board[indexR].append(decodeColors(color))
    
        indexR += 1

    grid = deepcopy(board)

    solvedBoard = await aStarSearch(board, websocket)
    
    
    

    await asyncio.sleep(0.1)  # Adjust delay as needed    

    return {"grid": solvedBoard}  # Same structure as your TS expects

from copy import deepcopy
import heapq

"""

Grid Like Game
User Places Barriers, It has to navigate the Player to one of the edges
User Places a goal and the player solves it


THINGS WE NEED

1. Transtion Model
    - Get player pos
    - Take Action Function
    - Get possible moves helper function

2. Heurstic Function
    - Thinking Manhattan Distance to Goal Square

3. Goal Test
    - Is the player at the Goal Cordinates?

4. A Star Search Function
"""

def returnCol(board, colNum, lower, upper):

    output = []

    for i in range(len(board)):

        if(i >= lower and i < upper):
            for j in range(len(board[0])):

                if(j == colNum):
                    output.append(board[i][j])
    
    return output

def makeMove(board, action):
    """Given a board state and an action moves the player, leaving a 'O' for visited Squares, 
    retruns new state if moove was successful"""
    x, y = getPlayerPos(board)
    
    
    match action:

        case 'U':
            board[y][x] = 'O'
            board[y-1][x] = 'p'
            return deepcopy(board)
        
        case 'D':
            board[y][x]= 'O'
            board[y+1][x] = 'p'
            return deepcopy(board)
        
        case 'L':
            board[y][x] = 'O'
            board[y][x-1] = 'p'
            return deepcopy(board)
        
        case 'R':
            board[y][x]= 'O'
            board[y][x+1] = 'p'   
            return deepcopy(board)

    return None

def getPossibleMoves(board):
    """Retruns a list of moves avaible to the player"""
    playerPos = getPlayerPos(board)
    x, y = playerPos

    possibleMoves = []
    
    rightBound = len(board[0]) - 1
    lowerBound = len(board) - 1

    #Boundary Checking
    if(x >= 0 and x < rightBound):
        if(not(board[y][x+1] == 'X')):
            possibleMoves.append('R')
            
    if(y > 0):
        if(not(board[y-1][x] == 'X')):
            possibleMoves.append('U')


    if(x <= rightBound and x > 0):
        if(not(board[y][x-1] == 'X')):
            possibleMoves.append("L")
    
    if(y < lowerBound):
        if(not(board[y+1][x] == 'X')):
            possibleMoves.append('D')

    return deepcopy(possibleMoves)

def getPlayerPos(board):
    """Returns a tuple (x,y) of the players postion on board"""
    x = 0
    y = 0

    for row in board:

        for col in row:

            if(col == 'p'):
                return (x, y)
            
            x += 1
        
        x = 0
        y += 1
    print("Player Not Found!")
    return (-1, -1)

def getGoalPos(board):
    """Returns a tuple (x,y) of the goal on board"""
    x = 0
    y = 0

    for row in board:

        for col in row:

            if(col == 'G'):
                return (x, y)
            
            x += 1
        
        x = 0
        y += 1
    print("Goal Not Found!")
    return (-1, -1)    

def printBoard(board):
    """Pretty prints a board"""
    
    for row in board:
        print('|', end = ' ')
        for col in row:
            print(col, end = ' ')
        print('|')

def generateBlankBoard(rows = 10, cols = 10, playerPos = (0,0)):
    """Generates a blank board, sets the player postion to 0 by default"""
    board = list()
    
    #Generates Board
    for i in range(rows):
        board.append(list())
        for j in range(cols):
            board[i].append("-")

    #Sets player Location
    x, y = playerPos

    if(y < rows and x < cols):
        board[y][x] = 'p'
    else:
        board[0][0] = 'p'
        print("Invalid PLayer Postion: Set Player Postion to (0,0)")


    return board

def placeBlock(board, x, y):
    """
    Used to place an obstacle on the boards.
    Returns board
    """
    
    if(x < len(board[0]) and y < len(board)):

        if(board[y][x] == 'X' or board[y][x] == 'p'):
            return None
        else:
            board[y][x] = 'X'
            return deepcopy(board)
    
    return None

def placeGoal(board, x, y):
    """
    Used to place a goal on the board
    Returns new updated board
    """
    if(x < len(board[0]) and y < len(board)):

        if(board[y][x] == 'G' or board[y][x] == 'p'):
            return None
        else:
            
            #Removes any other goals to ensure there is only one goal
            for row in board:
                for col in row:
                    if(col == 'G'):
                        col = '-'

            board[y][x] = 'G'
            return deepcopy(board)
    
    return False

def getAllPossibleStates(board, actions):
    """
    A function that returns a list of all possible states from given postion
    Uses two helpter functions, getPossibleMoves() and makeMove()
    """

    boardCopy = deepcopy(board)
    possibleStates = []
    
    if(len(actions) == 0):
        print("No Possible Moves")
        return []
    
    for move in actions:
        possibleStates.append(makeMove(boardCopy,move))
        boardCopy = deepcopy(board)

    return possibleStates

def removePath(board):

    for row in board:
        for col in row:
            if(col == 'O'):
                col = '-'

    return deepcopy(board)

def hFunc(board, goalPos):
    """
    Calculates the manhattan distance to the goal square.
    Checks for straight shots
    """
    route = []

    goalX, goalY = goalPos
    playerX, playerY = getPlayerPos(board)

    #If they are on the same row
    if(goalY == playerY):

        #if player is to the left of the goal
        if(playerX < goalX):
            
            #Sets row to the route being tested
            route = board[playerY][playerX:goalX]

        #if player is the right of the goal
        if(playerX > goalX):

            route = board[playerY][goalX:playerX]

        if('X' not in route):
            #If there is a clear shot, set the heurstic to 0
            return -10


    #If they are on the same col
    if(goalX == playerX):

        if(playerY < goalY):
            route = returnCol(board, goalX, playerY, goalY)

        if(playerY > goalY):
            route = returnCol(board, goalX, playerY, goalY)

        if('X' not in route):
        #If there is a clear shot, set the heurstic to 0
            return -10
   


    #Otherwise, return distance
    return ((abs(playerY - goalY)) + (abs(playerX - goalX))) 

def getJumpPoints(board):

    jumpPointStates= []

    playerX, playerY = getPlayerPos(board)
    playerPos = getPlayerPos(board)
    goalX, goalY = getGoalPos(board)

    #Checking for vetical jump points

    #First going up
    jumpPoint = (playerX, playerY)
    jumpBoard = deepcopy(board)

    #While player is not on the top layer and there is not a block
    while(jumpPoint[1] > 0 and not board[jumpPoint[0]][jumpPoint[1]] == 'X'):

        #Move jump point up
        jumpPoint = (playerX, jumpPoint[1] - 1)
        jumpBoard = makeMove(jumpBoard,'U')
        
    
    #if there is a new jump point
    if(not jumpPoint == playerPos):
        jumpPointStates.append(deepcopy(jumpBoard))


    #Second going down
    jumpPoint = playerPos
    jumpBoard = deepcopy(board)

    #While player is not on the top layer and there is not a block
    while(jumpPoint[1] < len(board) - 1 and not board[jumpPoint[0]][jumpPoint[1]] == 'X'):

        #Move jump point up
        jumpPoint = (playerX, jumpPoint[1] + 1)
        jumpBoard = makeMove(jumpBoard,'D')

    
    #if there is a new jump point
    if(not jumpPoint == playerPos):
        jumpPointStates.append(deepcopy(jumpBoard)) 
    

    #Third going left
    jumpPoint = playerPos
    jumpBoard = deepcopy(board)

    #While player is not on the top layer and there is not a block
    while(jumpPoint[0] > 0 and not board[jumpPoint[0]][jumpPoint[1]] == 'X'):

        #Move jump point up
        jumpPoint = (jumpPoint[0] - 1, playerY)
        jumpBoard = makeMove(jumpBoard,'L')

    
    #if there is a new jump point
    if(not jumpPoint == playerPos):
        jumpPointStates.append(deepcopy(jumpBoard)) 
    
    #Fourth going right
    jumpPoint = playerPos
    jumpBoard = deepcopy(board)

    #While player is not on the top layer and there is not a block
    while(jumpPoint[0] < len(board[0]) - 1 and not board[jumpPoint[0]][jumpPoint[1]] == 'X'):

        #Move jump point up
        jumpPoint = (jumpPoint[0] + 1, playerY)
        jumpBoard = makeMove(jumpBoard, 'R')

    #if there is a new jump point
    if(not jumpPoint == playerPos):
        jumpPointStates.append(deepcopy(jumpBoard)) 

    return jumpPointStates


def goalTest(board, goalPos):
    playerPos = getPlayerPos(board)
    
    if(playerPos == goalPos):
        return True
    
    return False

async def aStarSearch(board, websocket: WebSocket):

    frontier = []
    goalPos = getGoalPos(board)
    cost = hFunc(board, goalPos) + 0
    explored = list()
    maxNodes = 1000
    nodeExp = 0


    heapq.heappush(frontier, (cost, board, []))


    while frontier:


        curCost, currentBoard, curPath = heapq.heappop(frontier)
        nodeExp += 1

        if(goalTest(currentBoard, goalPos)):
            return currentBoard
        
        cleanedBoard = removePath(currentBoard)
        
        if cleanedBoard in explored:
            print("Explored")
            continue

        explored.append(deepcopy(cleanedBoard))

        possibleActions = getPossibleMoves(currentBoard)

        printBoard(currentBoard)

        if(len(curPath) > 0):
            lastMove = curPath[-1]

            if(lastMove == 'U' and 'D' in possibleActions):
                possibleActions.remove('D')
            if(lastMove == 'D' and 'U' in possibleActions):
                possibleActions.remove('U')
            if(lastMove == 'L' and 'R' in possibleActions):
                possibleActions.remove('R')
            if(lastMove == 'R' and 'L' in possibleActions):
                possibleActions.remove('L')
        
        # Send grid state to frontend via WebSocket
        
        # Simulate some delay to allow for visualization of each step

        #socket = active_connections[0]
        #await socket.send_json(currentBoard)

        await asyncio.sleep(0.001)  # Adjust delay as needed    
        await websocket.send_json(currentBoard)  # Send updated grid to front end

        
        possibleStates = getAllPossibleStates(currentBoard, possibleActions)

        newNode = zip(possibleActions, possibleStates)

        for action, state in newNode:
            newPath = deepcopy(curPath)
            newPath.append(action)
            newCost = (hFunc(state, goalPos)) + (len(newPath))

            heapq.heappush(frontier, (newCost, state, newPath))


def aStarSearchLocal(board):

    frontier = []
    goalPos = getGoalPos(board)
    cost = hFunc(board, goalPos) + 0
    explored = list()
    maxNodes = 1000
    nodeExp = 0


    heapq.heappush(frontier, (cost, board, []))


    while frontier:


        curCost, currentBoard, curPath = heapq.heappop(frontier)
        nodeExp += 1

        if(goalTest(currentBoard, goalPos)):
            return currentBoard
        
        cleanedBoard = removePath(currentBoard)
        
        if cleanedBoard in explored:
            print("Explored")
            continue

        explored.append(deepcopy(cleanedBoard))

        possibleActions = getPossibleMoves(currentBoard)

        printBoard(currentBoard)
        print('')

        if(len(curPath) > 0):
            lastMove = curPath[-1]

            if(lastMove == 'U' and 'D' in possibleActions):
                possibleActions.remove('D')
            if(lastMove == 'D' and 'U' in possibleActions):
                possibleActions.remove('U')
            if(lastMove == 'L' and 'R' in possibleActions):
                possibleActions.remove('R')
            if(lastMove == 'R' and 'L' in possibleActions):
                possibleActions.remove('L')
        
        # Send grid state to frontend via WebSocket
        
        # Simulate some delay to allow for visualization of each step

        #socket = active_connections[0]
        #await socket.send_json(currentBoard
        
        possibleStates = getAllPossibleStates(currentBoard, possibleActions)

        newNode = zip(possibleActions, possibleStates)

        for action, state in newNode:
            newPath = deepcopy(curPath)
            newPath.append(action)
            newCost = (hFunc(state, goalPos)) + (len(newPath))

            heapq.heappush(frontier, (newCost, state, newPath))

async def aStarSearchwJP(board, websocket: WebSocket):

    frontier = []
    goalPos = getGoalPos(board)
    cost = hFunc(board, goalPos) + 0
    explored = list()
    maxNodes = 1000
    nodeExp = 0


    heapq.heappush(frontier, (cost, board, []))


    while frontier:


        curCost, currentBoard, curPath = heapq.heappop(frontier)
        nodeExp += 1

        if(goalTest(currentBoard, goalPos)):
            return currentBoard
        
        cleanedBoard = removePath(currentBoard)
        
        if cleanedBoard in explored:
            print("Explored")
            continue

        explored.append(deepcopy(cleanedBoard))

        possibleActions = getPossibleMoves(currentBoard)

        printBoard(currentBoard)

        if(len(curPath) > 0):
            lastMove = curPath[-1]

            if(lastMove == 'U' and 'D' in possibleActions):
                possibleActions.remove('D')
            if(lastMove == 'D' and 'U' in possibleActions):
                possibleActions.remove('U')
            if(lastMove == 'L' and 'R' in possibleActions):
                possibleActions.remove('R')
            if(lastMove == 'R' and 'L' in possibleActions):
                possibleActions.remove('L')
   
        await asyncio.sleep(0.05)  # Adjust delay as needed    
        await websocket.send_json(currentBoard)  # Send updated grid to front end

        
        possibleStates = getJumpPoints(currentBoard)

        newNode = zip(possibleActions, possibleStates)

        for action, state in newNode:
            newPath = deepcopy(curPath)
            newPath.append(action)
            newCost = (hFunc(state, goalPos)) + (len(newPath))

            heapq.heappush(frontier, (newCost, state, newPath))
