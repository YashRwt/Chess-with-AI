

import pygame 
import pickle 
from pygame.locals import * 
import copy 
import threading 
from collections import defaultdict 
import random 
from collections import Counter 
import os 

class GamePosition:
    def __init__(self,chessbrd,player,castling_rights,EnP_Target,HMC,history = {}):
        self.chessbrd = chessbrd 
        self.player = player 
        self.castling = castling_rights 
        self.EnP = EnP_Target 
        self.HMC = HMC 
        self.history = history 
        
    def getchessbrd(self):
        return self.chessbrd
    def setchessbrd(self,chessbrd):
        self.chessbrd = chessbrd
    def getplayer(self):
        return self.player
    def setplayer(self,player):
        self.player = player
    def getCastleRights(self):
        return self.castling
    def setCastleRights(self,castling_rights):
        self.castling = castling_rights
    def getEnP(self):
        return self.EnP
    def setEnP(self, EnP_Target):
        self.EnP = EnP_Target
    def getHMC(self):
        return self.HMC
    def setHMC(self,HMC):
        self.HMC = HMC
    def checkRepition(self):
        return any(value>=3 for value in self.history.values())
    def addtoHistory(self,position):
        key = generatekey(position)
        self.history[key] = self.history.get(key,0) + 1
    def gethistory(self):
        return self.history
    def clone(self):
        clone = GamePosition(copy.deepcopy(self.chessbrd),
                             self.player,
                             copy.deepcopy(self.castling), 
                             self.EnP,
                             self.HMC)
        return clone
       
class Shades:
    def __init__(self,image,coord):
        self.image = image
        self.pos = coord
    def retrivecordinates(self):
        return [self.image,self.pos]
    
class Piece:
    def __init__(self,pieceinfo,chess_coord):
        piece = pieceinfo[0]
        color = pieceinfo[1]

        if piece=='K':
            index = 0
        elif piece=='Q':
            index = 1
        elif piece=='B':
            index = 2
        elif piece == 'N':
            index = 3
        elif piece == 'R':
            index = 4
        elif piece == 'P':
            index = 5
        left_x = widthofsquare*index
        if color == 'w':
            left_y = 0
        else:
            left_y = heightofsquare
        
        self.pieceinfo = pieceinfo
        self.subsection = (left_x,left_y,widthofsquare,heightofsquare)
        self.chess_coord = chess_coord
        self.pos = (-1,-1)

    def retrivecordinates(self):
        return [self.chess_coord, self.subsection,self.pos]
    def updatepositions(self,pos):
        self.pos = pos
    def retrivepositions(self):
        return self.pos
    def updatecordinates(self,coord):
        self.chess_coord = coord
    def __repr__(self):
        return self.pieceinfo+'('+str(chess_coord[0])+','+str(chess_coord[1])+')'

##################################/////CHESS PROCESSING FUNCTIONS\\\\########################

def drawingtxt(chessbrd):
    for i in range(len(chessbrd)):
        for k in range(len(chessbrd[i])):
            if chessbrd[i][k]==0:
                chessbrd[i][k] = 'Oo'
        print (chessbrd[i])
    for i in range(len(chessbrd)):
        for k in range(len(chessbrd[i])):
            if chessbrd[i][k]=='Oo':
                chessbrd[i][k] = 0
                
def ispiecepresentby(chessbrd,x,y,color):
    x = int(x)
    y = int(y)
    if chessbrd[y][x] == 0:
        return False
    if chessbrd[y][x][1] == color[0]:
        return True
    return False                

def ispiecepresent(chessbrd,x,y):
    x = int(x)
    y = int(y)
    if chessbrd[y][x] == 0:        
        return False
    return True

def colorFilter(chessbrd,listofTuples,color):
    filtered_list = []
    for pos in listofTuples:
        x = pos[0]
        y = pos[1]
        x = int(x)
        y = int(y)
        if x>=0 and x<=7 and y>=0 and y<=7 and not ispiecepresentby(chessbrd,x,y,color):

            filtered_list.append(pos)
    return filtered_list

def underAttack(position,target_x,target_y,color):

    chessbrd = position.getchessbrd()
    color = color[0]
    listofAttackedSquares = []
    for x in range(8):
        for y in range(8):
            if chessbrd[y][x]!=0 and chessbrd[y][x][1]==color:
                listofAttackedSquares.extend(
                    getAllblocks(position,x,y,True))
    return (target_x,target_y) in listofAttackedSquares 

def findmypiece(chessbrd,piece):
    listofLocations = []
    for row in range(8):
        for col in range(8):
            if chessbrd[row][col] == piece:
                x = col
                y = row
                listofLocations.append((x,y))
    return listofLocations 
           
def getAllblocks(position,x,y,AttackSearch=False):
    x = int(x)
    y = int(y)
    chessbrd = position.getchessbrd()
    player = position.getplayer()
    castling_rights = position.getCastleRights()
    EnP_Target = position.getEnP()
    if len(chessbrd[y][x])!=2:
        return [] 
    piece = chessbrd[y][x][0] 
    color = chessbrd[y][x][1] 
    enemy_color = getthep(color)
    listofTuples = []

    if piece == 'P': 
        if color=='w': 
            if not ispiecepresent(chessbrd,x,y-1) and not AttackSearch:
                listofTuples.append((x,y-1))
                if y == 6 and not ispiecepresent(chessbrd,x,y-2):
                    listofTuples.append((x,y-2))
            if x!=0 and ispiecepresentby(chessbrd,x-1,y-1,'black'):
                listofTuples.append((x-1,y-1))
            if x!=7 and ispiecepresentby(chessbrd,x+1,y-1,'black'):
                listofTuples.append((x+1,y-1))
            if EnP_Target!=-1: 
                if EnP_Target == (x-1,y-1) or EnP_Target == (x+1,y-1):
                    listofTuples.append(EnP_Target)
            
        elif color=='b': 
            if not ispiecepresent(chessbrd,x,y+1) and not AttackSearch:
                listofTuples.append((x,y+1))
                if y == 1 and not ispiecepresent(chessbrd,x,y+2):
                    listofTuples.append((x,y+2))
            if x!=0 and ispiecepresentby(chessbrd,x-1,y+1,'white'):
                listofTuples.append((x-1,y+1))
            if x!=7 and ispiecepresentby(chessbrd,x+1,y+1,'white'):
                listofTuples.append((x+1,y+1))
            if EnP_Target == (x-1,y+1) or EnP_Target == (x+1,y+1):
                listofTuples.append(EnP_Target)

    elif piece == 'R': 
        for i in [-1,1]:
            kx = x 
            while True: 
                kx = kx + i 
                if kx<=7 and kx>=0:                     
                    if not ispiecepresent(chessbrd,kx,y):                       
                        listofTuples.append((kx,y))
                    else:                        
                        if ispiecepresentby(chessbrd,kx,y,enemy_color):
                            listofTuples.append((kx,y))
                        break                        
                else: 
                    break
        for i in [-1,1]:
            ky = y
            while True:
                ky = ky + i 
                if ky<=7 and ky>=0: 
                    if not ispiecepresent(chessbrd,x,ky):
                        listofTuples.append((x,ky))
                    else:
                        if ispiecepresentby(chessbrd,x,ky,enemy_color):
                            listofTuples.append((x,ky))
                        break
                else:
                    break
        
    elif piece == 'N': 
        for dx in [-2,-1,1,2]:
            if abs(dx)==1:
                sy = 2
            else:
                sy = 1
            for dy in [-sy,+sy]:
                listofTuples.append((x+dx,y+dy))
        listofTuples = colorFilter(chessbrd,listofTuples,color)
    elif piece == 'B': 
        for dx in [-1,1]: 
            for dy in [-1,1]: 
                kx = x 
                ky = y
                while True: 
                    kx = kx + dx 
                    ky = ky + dy 
                    if kx<=7 and kx>=0 and ky<=7 and ky>=0:
                        if not ispiecepresent(chessbrd,kx,ky):
                            listofTuples.append((kx,ky))
                        else:
                            if ispiecepresentby(chessbrd,kx,ky,enemy_color):
                                listofTuples.append((kx,ky))
                            break    
                    else:
                        break
    
    elif piece == 'Q': #For the queen
        chessbrd[y][x] = 'R' + color
        list_rook = getAllblocks(position,x,y,True)
        chessbrd[y][x] = 'B' + color
        list_bishop = getAllblocks(position,x,y,True)
        listofTuples = list_rook + list_bishop

        chessbrd[y][x] = 'Q' + color
        
    elif piece == 'K': # A king!
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                listofTuples.append((x+dx,y+dy))
        listofTuples = colorFilter(chessbrd,listofTuples,color)
        if not AttackSearch:
            right = castling_rights[player]
            if (right[0] and 
            chessbrd[y][7]!=0 and 
            chessbrd[y][7][0]=='R' and 
            not ispiecepresent(chessbrd,x+1,y) and 
            not ispiecepresent(chessbrd,x+2,y) and 
            not underAttack(position,x,y,enemy_color) and 
            not underAttack(position,x+1,y,enemy_color) and 
            not underAttack(position,x+2,y,enemy_color)):
                listofTuples.append((x+2,y))
            if (right[1] and 
            chessbrd[y][0]!=0 and 
            chessbrd[y][0][0]=='R' and 
            not ispiecepresent(chessbrd,x-1,y)and 
            not ispiecepresent(chessbrd,x-2,y)and 
            not ispiecepresent(chessbrd,x-3,y) and 
            not underAttack(position,x,y,enemy_color) and 
            not underAttack(position,x-1,y,enemy_color) and 
            not underAttack(position,x-2,y,enemy_color)):
                listofTuples.append((x-2,y)) 
    if not AttackSearch:
        new_list = []
        for tupleq in listofTuples:
            x2 = tupleq[0]
            y2 = tupleq[1]
            temp_pos = position.clone()
            dispplaythemove(temp_pos,x,y,x2,y2)
            if not kingInCheck(temp_pos,color):
                new_list.append(tupleq)
        listofTuples = new_list
    return listofTuples

def getthep(color):
    color = color[0]
    if color == 'w':
        getthepcolor = 'b'
    else:
        getthepcolor = 'w'
    return getthepcolor

def dispplaythemove(position,x,y,x2,y2):
    x2 = int(x2)
    y2= int(y2)
    chessbrd = position.getchessbrd()
    piece = chessbrd[y][x][0]
    color = chessbrd[y][x][1]
    player = position.getplayer()
    castling_rights = position.getCastleRights()
    EnP_Target = position.getEnP()
    half_move_clock = position.getHMC()
    if ispiecepresent(chessbrd,x2,y2) or piece=='P':
        half_move_clock = 0
    else:
        half_move_clock += 1
    chessbrd[y2][x2] = chessbrd[y][x]
    chessbrd[y][x] = 0    
    if piece == 'K':
        castling_rights[player] = [False,False]
        if abs(x2-x) == 2:
            if color=='w':
                l = 7
            else:
                l = 0
            if x2>x:
                    chessbrd[l][5] = 'R'+color
                    chessbrd[l][7] = 0
            else:
                    chessbrd[l][3] = 'R'+color
                    chessbrd[l][0] = 0

    if piece=='R':#for the Rook
        if x==0 and y==0:
            castling_rights[1][1] = False
        elif x==7 and y==0:
            castling_rights[1][0] = False
        elif x==0 and y==7:
            castling_rights[0][1] = False
        elif x==7 and y==7:
            castling_rights[0][0] = False

    if piece == 'P':#For the Pawn
        if EnP_Target == (x2,y2):
            if color=='w':
                chessbrd[y2+1][x2] = 0
            else:
                chessbrd[y2-1][x2] = 0
        if abs(y2-y)==2:
            EnP_Target = (x,(y+y2)/2)
        else:
            EnP_Target = -1
        if y2==0:
            chessbrd[y2][x2] = 'Qw'
        elif y2 == 7:
            chessbrd[y2][x2] = 'Qb'
    else:
        EnP_Target = -1
    player = 1 - player          
    position.setplayer(player)
    position.setCastleRights(castling_rights)
    position.setEnP(EnP_Target)
    position.setHMC(half_move_clock)

def kingInCheck(position,color):
    chessbrd = position.getchessbrd()
    color = color[0]
    enemy = getthep(color)
    piece = 'K' + color

    x,y = findmypiece(chessbrd,piece)[0]
    x = int(x)
    y = int(y)
    return underAttack(position,x,y,enemy)

def isStalemate(position):
    player = position.getplayer()
    if player==0:
        color = 'w'
    else:
        color = 'b'
    if not kingInCheck(position,color) and outcomesGenerated(position,color)==[]:
        return True
    return False

def CheckCHKMTE(position,color=-1):
    
    if color==-1:
        return CheckCHKMTE(position,'white') or CheckCHKMTE(position,'b')
    color = color[0]
    if kingInCheck(position,color) and outcomesGenerated(position,color)==[]:
            return True
    return False

def allpiecescalled(position,color):
    chessbrd = position.getchessbrd()
    listofpos = []
    for j in range(8):
        for i in range(8):
            if ispiecepresentby(chessbrd,i,j,color):
                listofpos.append((i,j))
    return listofpos

def generatekey(position):
    #Get chessbrd:
    chessbrd = position.getchessbrd()
    chessbrdTuple = []
    for row in chessbrd:
        chessbrdTuple.append(tuple(row))
    chessbrdTuple = tuple(chessbrdTuple)
    rights = position.getCastleRights()
    tuplerights = (tuple(rights[0]),tuple(rights[1]))
    key = (chessbrdTuple,position.getplayer(),
           tuplerights)
    return key

def outcomesGenerated(position, color):
    if color==1:
        color = 'white'
    elif color ==-1:
        color = 'black'
    color = color[0]
    listofpieces = allpiecescalled(position,color)
    moves = []
    for pos in listofpieces:
        targets = getAllblocks(position,pos[0],pos[1])
        for target in targets:
             moves.append([pos,target])
    return moves

##############################////////GUI FUNCTIONS\\\\\\\\\\\\\#############################
def getpixel(chess_coord):
    x,y = chess_coord
    if aiChoice:
        if plyr_ai==0:
            return ((7-x)*widthofsquare, (7-y)*heightofsquare)
        else:
            return (x*widthofsquare, y*heightofsquare)
    if not flipChoice or player==0 ^ gettransition:
        return (x*widthofsquare, y*heightofsquare)
    else:
        return ((7-x)*widthofsquare, (7-y)*heightofsquare)
    
def itemInfo(chess_coord):
    for piece in whiteItemList+blackItemList:
        if piece.retrivecordinates()[0] == chess_coord:
            return piece
    
def getBoxNO(pixel_coord):
    x,y = pixel_coord[0]/widthofsquare, pixel_coord[1]/heightofsquare
    x = int(get_digit(x, 0))
    y = int(get_digit(y, 0)) 
    if aiChoice:
        if plyr_ai==0:
            return (7-x,7-y)
        else:
            return (x,y)
    if not flipChoice or player==0 ^ gettransition:
        return (x,y)
    else:
        return (7-x,7-y)
    
def renderItem(chessbrd):
    whiteItemList = []
    blackItemList = []
    for i in range(8):
        for k in range(8):
            if chessbrd[i][k]!=0:
                p = Piece(chessbrd[i][k],(k,i))
                if chessbrd[i][k][1]=='w':
                    whiteItemList.append(p)
                else:
                    blackItemList.append(p)
    return [whiteItemList,blackItemList]

def renderMaze():
    displayy.blit(bkgrnd,(0,0))
    if player==1:
        order = [whiteItemList,blackItemList]
    else:
        order = [blackItemList,whiteItemList]
    if gettransition:
        order = list(reversed(order))
    if checkfordraw or gamefinished or gameprocessing:
        for shade in listofShades:
            img,chess_coord = shade.retrivecordinates()
            pixel_coord = getpixel(chess_coord)
            displayy.blit(img,pixel_coord)
    if previouschnce[0]!=-1 and not gettransition:
        x,y,x2,y2 = previouschnce
        displayy.blit(yellowbox_image,getpixel((x,y)))
        displayy.blit(yellowbox_image,getpixel((x2,y2)))

    for piece in order[0]:
        
        chess_coord,subsection,pos = piece.retrivecordinates()
        pixel_coord = getpixel(chess_coord)
        if pos==(-1,-1):
            displayy.blit(item_image,pixel_coord,subsection)
        else:
            displayy.blit(item_image,pos,subsection)

    if not (checkfordraw or gamefinished or gameprocessing):
        for shade in listofShades:
            img,chess_coord = shade.retrivecordinates()
            pixel_coord = getpixel(chess_coord)
            displayy.blit(img,pixel_coord)

    for piece in order[1]:
        chess_coord,subsection,pos = piece.retrivecordinates()
        pixel_coord = getpixel(chess_coord)
        if pos==(-1,-1):
            displayy.blit(item_image,pixel_coord,subsection)
        else:
            displayy.blit(item_image,pos,subsection)

def impo1function(listofTuples):
    global listofShades
    listofShades = []
    if gettransition:
        return
    if checkfordraw:
        coord = findmypiece(chessbrd,'Kw')[0]
        shade = Shades(bigYellowDot,coord)
        listofShades.append(shade)
        coord = findmypiece(chessbrd,'Kb')[0]
        shade = Shades(bigYellowDot,coord)
        listofShades.append(shade)
        return
    if gamefinished:
        coord = findmypiece(chessbrd,'K'+winner)[0]
        shade = Shades(bigGreenDot,coord)
        listofShades.append(shade)
    if kingInCheck(position,'white'):
        coord = findmypiece(chessbrd,'Kw')[0]
        shade = Shades(bigRedDot,coord)
        listofShades.append(shade)
    if kingInCheck(position,'black'):
        coord = findmypiece(chessbrd,'Kb')[0]
        shade = Shades(bigRedDot,coord)
        listofShades.append(shade)
    for pos in listofTuples:
        if ispiecepresent(chessbrd,pos[0],pos[1]):
            img = green_dot
        else:
            img = green_dot_small
        shade = Shades(img,pos)
        listofShades.append(shade)
        

#********************************* FUNCTIONS RELATED to Ai *********************************#

def generateNewMove(position,depth,alpha,beta,colorsign,bestMoveReturn,root=True):
    if root:
        key = generatekey(position)
        if key in gamewindow:
            bestMoveReturn[:] = random.choice(gamewindow[key])
            return
    global serachdone
    if depth==0:
        return colorsign*getEval(position)
    moves = outcomesGenerated(position, colorsign)
    if moves==[]:
        return colorsign*getEval(position)
    if root:
        bestMove = moves[0]
    bestValue = -100000
    for move in moves:
        newpos = position.clone()
        dispplaythemove(newpos,move[0][0],move[0][1],move[1][0],move[1][1])
        key = generatekey(newpos)
        if key in serachdone:
            value = serachdone[key]
        else:
            value = -generateNewMove(newpos,depth-1, -beta,-alpha,-colorsign,[],False)
            serachdone[key] = value
        if value>bestValue:
            bestValue = value
            if root:
                bestMove = move
        alpha = max(alpha,value)
        if alpha>=beta:
            break
    if root:
        serachdone = {}
        bestMoveReturn[:] = bestMove
        return
    return bestValue

def getscore(flatchessbrd, gamephase):
    score=0
    for i in range(64):
        if flatchessbrd[i] == 0:
            continue
        piece = flatchessbrd[i][0]
        color = flatchessbrd[i][1]
        sign = +1
        if color == 'b':
            row = 7 - i // 8
            col = i % 8
            i = row * 8 + col
            sign = -1
        if piece == 'P':
            score += sign * soilder_table[i]
        elif piece == 'N':
            score += sign * horse_table[i]
        elif piece == 'B':
            score += sign * int(camel_table[i])
        elif piece == 'R':
            score += sign * elephant_table[i]
        elif piece == 'Q':
            score += sign * general_table[i]
        elif piece == 'K':
            if gamephase == 'opening':
                score += sign * emperor_table[i]
            else:
                score += sign * ending_t[i]
    return score

def getEval(position):
    if CheckCHKMTE(position,'white'):
        return -20000
    if CheckCHKMTE(position,'black'):
        return 20000
    chessbrd = position.getchessbrd()
    flatchessbrd = [x for row in chessbrd for x in row]
    c = Counter(flatchessbrd)
    Qw = c['Qw']
    Qb = c['Qb']
    Rw = c['Rw']
    Rb = c['Rb']
    Bw = c['Bw']
    Bb = c['Bb']
    Nw = c['Nw']
    Nb = c['Nb']
    Pw = c['Pw']
    Pb = c['Pb']
    whiteMaterial = 9*Qw + 5*Rw + 3*Nw + 3*Bw + 1*Pw
    blackMaterial = 9*Qb + 5*Rb + 3*Nb + 3*Bb + 1*Pb
    numofmoves = len(position.gethistory())
    gamephase = 'opening'
    if numofmoves>40 or (whiteMaterial<14 and blackMaterial<14):
        gamephase = 'ending'
    Dw = function2(chessbrd,'white')
    Db = function2(chessbrd,'black')
    Sw = lockedpiece(chessbrd,'white')
    Sb = lockedpiece(chessbrd,'black')
    Iw = indangerpiece(chessbrd,'white')
    Ib = indangerpiece(chessbrd,'black')
    evaluation1 = 900*(Qw - Qb) + 500*(Rw - Rb) +330*(Bw-Bb
                )+320*(Nw - Nb) +100*(Pw - Pb) +-30*(Dw-Db + Sw-Sb + Iw- Ib
                )
    evaluation2 = getscore(flatchessbrd,gamephase)
    evaluation = evaluation1 + evaluation2
    return evaluation

def function2(chessbrd,color):
    color = color[0]
    listofpawns = findmypiece(chessbrd,'P'+color)
    repeats = 0
    temp = []
    for pawnpos in listofpawns:
        if pawnpos[0] in temp:
            repeats = repeats + 1
        else:
            temp.append(pawnpos[0])
    return repeats

def indangerpiece(chessbrd,color):
    color = color[0]
    listofpawns = findmypiece(chessbrd,'P'+color)
    xlist = [x for (x,y) in listofpawns]
    isolated = 0
    for x in xlist:
        if x!=0 and x!=7:
            if x-1 not in xlist and x+1 not in xlist:
                isolated+=1
        elif x==0 and 1 not in xlist:
            isolated+=1
        elif x==7 and 6 not in xlist:
            isolated+=1
    return isolated

def get_digit(number, n):
    return number // 10**n % 10

def lockedpiece(chessbrd,color):
    color = color[0]
    listofpawns = findmypiece(chessbrd,'P'+color)
    blocked = 0
    for pawnpos in listofpawns:
        if ((color=='w' and ispiecepresentby(chessbrd,pawnpos[0],pawnpos[1]-1,
                                       'black'))
            or (color=='b' and ispiecepresentby(chessbrd,pawnpos[0],pawnpos[1]+1,
                                       'white'))):
            blocked = blocked + 1
    return blocked



#*********************************IINITIALIZING THE CHESSBOARD*********************************#

print(int(56),float(56))
chessbrd = [ ['Rb', 'Nb', 'Bb', 'Qb', 'Kb', 'Bb', 'Nb', 'Rb'], #8
          ['Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb', 'Pb'], #7
          [  0,    0,    0,    0,    0,    0,    0,    0],  #6
          [  0,    0,    0,    0,    0,    0,    0,    0],  #5
          [  0,    0,    0,    0,    0,    0,    0,    0],  #4
          [  0,    0,    0,    0,    0,    0,    0,    0],  #3
          ['Pw', 'Pw', 'Pw',  'Pw', 'Pw', 'Pw', 'Pw', 'Pw'], #2
          ['Rw', 'Nw', 'Bw',  'Qw', 'Kw', 'Bw', 'Nw', 'Rw'] ]#1
          # a      b     c     d     e     f     g     h


player = 0
castling_rights = [[True, True],[True, True]]

En_Passant_Target = -1 
half_move_clock = 0 
position = GamePosition(chessbrd,player,castling_rights,En_Passant_Target
                        ,half_move_clock)
soilder_table = [  0,  0,  0,  0,  0,  0,  0,  0, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 20, 30, 30, 20, 10, 10, 5,  5, 10, 25, 25, 10,  5,  5, 0,  0,  0, 20, 20,  0,  0,  0, 5, -5,-10,  0,  0,-10, -5,  5, 5, 10, 10,-20,-20, 10, 10,  5, 0,  0,  0,  0,  0,  0,  0,  0]
horse_table = [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,  0,  0,  0,  0,-20,-40,-30,  0, 10, 15, 15, 10,  0,-30,-30,  5, 15, 20, 20, 15,  5,-30,-30,  0, 15, 20, 20, 15,  0,-30,-30,  5, 10, 15, 15, 10,  5,-30,-40,-20,  0,  5,  5,  0,-20,-40,-50,-90,-30,-30,-30,-30,-90,-50]
camel_table = [-20,-10,-10,-10,-10,-10,-10,-20,-10,  0,  0,  0,  0,  0,  0,-10,-10,  0,  5, 10, 10,  5,  0,-10,-10,  5,  5, 10, 10,  5,  5,-10,-10,  0, 10, 10, 10, 10,  0,-10,-10, 10, 10, 10, 10, 10, 10,-10,-10,  5,  0,  0,  0,  0,  5,-10,-20,-10,-90,-10,-10,-90,-10,-20]
elephant_table = [0,  0,  0,  0,  0,  0,  0,  0, 5, 10, 10, 10, 10, 10, 10,  5, -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5, -5,  0,  0,  0,  0,  0,  0, -5,  0,  0,  0,  5,  5,  0,  0,  0]
general_table = [-20,-10,-10, -5, -5,-10,-10,-20,-10,  0,  0,  0,  0,  0,  0,-10,-10,  0,  5,  5,  5,  5,  0,-10, -5,  0,  5,  5,  5,  5,  0, -5,  0,  0,  5,  5,  5,  5,  0, -5,-10,  5,  5,  5,  5,  5,  0,-10,-10,  0,  5,  0,  0,  0,  0,-10,-20,-10,-10, 70, -5,-10,-10,-20]
emperor_table = [-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10, 20, 20,  0,  0,  0,  0, 20, 20, 20, 30, 10,  0,  0, 10, 30, 20]
ending_t = [-50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,  0,  0,-10,-20,-30,-30,-10, 20, 30, 30, 20,-10,-30,-30,-10, 30, 40, 40, 30,-10,-30,-30,-10, 30, 40, 40, 30,-10,-30,-30,-10, 20, 30, 30, 20,-10,-30,-30,-30,  0,  0,  0,  0,-30,-30,-50,-30,-30,-30,-30,-30,-30,-50]

pygame.init()
displayy = pygame.display.set_mode((600,600))
bkgrnd = pygame.image.load(os.path.join('images','board.png')).convert()
item_image = pygame.image.load(os.path.join('images','Chess_Pieces_Sprite.png')).convert_alpha()
green_dot_small = pygame.image.load(os.path.join('images','green_circle_small.png')).convert_alpha()
green_dot = pygame.image.load(os.path.join('images','green_circle_neg.png')).convert_alpha()
bigRedDot = pygame.image.load(os.path.join('images','red_circle_big.png')).convert_alpha()
greenbox_image = pygame.image.load(os.path.join('images','green_box.png')).convert_alpha()
bigYellowDot = pygame.image.load(os.path.join('images','yellow_circle_big.png')).convert_alpha()
bigGreenDot = pygame.image.load(os.path.join('images','green_circle_big.png')).convert_alpha()
yellowbox_image = pygame.image.load(os.path.join('images','yellow_box.png')).convert_alpha()
withfriend_pic = pygame.image.load(os.path.join('images','withfriend.png')).convert_alpha()
aiImg = pygame.image.load(os.path.join('images','withAI.png')).convert_alpha()
white1 = pygame.image.load(os.path.join('images','playWhite.png')).convert_alpha()
black1 = pygame.image.load(os.path.join('images','playBlack.png')).convert_alpha()
eabledflip = pygame.image.load(os.path.join('images','flipEnabled.png')).convert_alpha()
disabledflip = pygame.image.load(os.path.join('images','flipDisabled.png')).convert_alpha()
backgroundsize = bkgrnd.get_rect().size
widthofsquare = backgroundsize[0]/8
heightofsquare = backgroundsize[1]/8
item_image = pygame.transform.scale(item_image,
                                      (widthofsquare*6,heightofsquare*2))
green_dot_small = pygame.transform.scale(green_dot_small,
                                      (widthofsquare, heightofsquare))
green_dot = pygame.transform.scale(green_dot,
                                      (widthofsquare, heightofsquare))
bigRedDot = pygame.transform.scale(bigRedDot,
                                      (widthofsquare, heightofsquare))
greenbox_image = pygame.transform.scale(greenbox_image,
                                      (widthofsquare, heightofsquare))
yellowbox_image = pygame.transform.scale(yellowbox_image,
                                      (widthofsquare, heightofsquare))
bigYellowDot = pygame.transform.scale(bigYellowDot,
                                             (widthofsquare, heightofsquare))
bigGreenDot = pygame.transform.scale(bigGreenDot,
                                             (widthofsquare, heightofsquare))
withfriend_pic = pygame.transform.scale(withfriend_pic,
                                      (widthofsquare*4,heightofsquare*4))
aiImg = pygame.transform.scale(aiImg,
                                      (widthofsquare*4,heightofsquare*4))
white1 = pygame.transform.scale(white1,
                                      (widthofsquare*4,heightofsquare*4))
black1 = pygame.transform.scale(black1,
                                      (widthofsquare*4,heightofsquare*4))
eabledflip = pygame.transform.scale(eabledflip,
                                      (widthofsquare*4,heightofsquare*4))
disabledflip = pygame.transform.scale(disabledflip,
                                      (widthofsquare*4,heightofsquare*4))
displayy = pygame.display.set_mode(backgroundsize)
pygame.display.set_caption('Shallow Green')
displayy.blit(bkgrnd,(0,0))
whiteItemList,blackItemList = renderItem(chessbrd)
listofShades = []

clock = pygame.time.Clock()
downward = False
getinput = False
gettransition = False
checkfordraw = False 
gamefinished = False 
gamerecord = False 
gameprocessing = False 
gamewindow = defaultdict(list)
try:
    file_handle = open('records.txt','r+')
    gamewindow = pickle.loads(file_handle.read())
except:
    if gamerecord:
        file_handle = open('records.txt','w')

serachdone = {} 
previouschnce = [-1,-1,-1,-1] 
ax,ay=0,0
number = 0
menuChoice = True
aiChoice = -1
flipChoice = -1
plyr_ai = -1
gameEnded = False
#*********************************INFINITLY LOOPING*********************************#
while not gameEnded:
    if menuChoice:
        displayy.blit(bkgrnd,(0,0))
        if aiChoice==-1:
            displayy.blit(withfriend_pic,(0,heightofsquare*2))
            displayy.blit(aiImg,(widthofsquare*4,heightofsquare*2))
        elif aiChoice==True:
            displayy.blit(white1,(0,heightofsquare*2))
            displayy.blit(black1,(widthofsquare*4,heightofsquare*2))
        elif aiChoice==False:
            displayy.blit(disabledflip,(0,heightofsquare*2))
            displayy.blit(eabledflip,(widthofsquare*4,heightofsquare*2))
        if flipChoice!=-1:
            renderMaze()

            menuChoice = False
            if aiChoice and plyr_ai==0:
                colorsign=1
                bestMoveReturn = []
                move_thread = threading.Thread(target = generateNewMove,
                            args = (position,3,-1000000,1000000,colorsign,bestMoveReturn))
                move_thread.start()
                gameprocessing = True
            continue
        for event in pygame.event.get():
            if event.type==QUIT:
                gameEnded = True
                break
            if event.type == MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if (pos[0]<widthofsquare*4 and
                pos[1]>heightofsquare*2 and
                pos[1]<heightofsquare*6):
                    if aiChoice == -1:
                        aiChoice = False
                    elif aiChoice==True:
                        plyr_ai = 1
                        flipChoice = False
                    elif aiChoice==False:
                        flipChoice = False
                elif (pos[0]>widthofsquare*4 and
                pos[1]>heightofsquare*2 and
                pos[1]<heightofsquare*6):
                    if aiChoice == -1:
                        aiChoice = True
                    elif aiChoice==True:
                        plyr_ai = 0
                        flipChoice = False
                    elif aiChoice==False:
                        flipChoice=True

        pygame.display.update()

        clock.tick(60)
        continue

    number+=1
    if gameprocessing and number%6==0:
        ax+=1
        if ax==8:
            ay+=1
            ax=0
        if ay==8:
            ax,ay=0,0
        if ax%4==0:
            impo1function([])
        if plyr_ai==0:
            listofShades.append(Shades(greenbox_image,(7-ax,7-ay)))
        else:
            listofShades.append(Shades(greenbox_image,(ax,ay)))
    
    for event in pygame.event.get():
        if event.type==QUIT:
            gameEnded = True        
            break

        if gamefinished or gettransition or gameprocessing:
            continue

        if not downward and event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            chess_coord = getBoxNO(pos)
            a = chess_coord[0]
            b = chess_coord[1]
            x= get_digit(int(a), 0)
            y= get_digit(int(b), 0)
            if not ispiecepresentby(chessbrd,x,y,'wb'[player]):
                continue
            dragPiece = itemInfo(chess_coord)
            listofTuples = getAllblocks(position,x,y)
            impo1function(listofTuples)
            if ((dragPiece.pieceinfo[0]=='K') and
                (kingInCheck(position,'white') or kingInCheck(position,'black'))):
                None
            else:
                listofShades.append(Shades(greenbox_image,(x,y)))
            downward = True       
        if (downward or getinput) and event.type == MOUSEBUTTONUP:
            downward = False
            dragPiece.updatepositions((-1,-1))
            pos = pygame.mouse.get_pos()
            chess_coord = getBoxNO(pos)
            x2 = chess_coord[0]
            y2 = chess_coord[1]
            x2= int(x2)
            y2= int(y2)

            gettransition = False
            if (x,y)==(x2,y2): 
                if not getinput:
                    getinput = True
                    prevPos = (x,y)
                else:
                    x,y = prevPos
                    if (x,y)==(x2,y2): 
                        getinput = False
                        impo1function([])
                    else:
                        if ispiecepresentby(chessbrd,x2,y2,'wb'[player]):
                            getinput = True
                            prevPos = (x2,y2)
                        else:
                            getinput = False
                            impo1function([])
                            gettransition = True
                            

            if not (x2,y2) in listofTuples:
                gettransition = False
                continue
            
            if gamerecord:
                key = generatekey(position)
                if [(x,y),(x2,y2)] not in gamewindow[key]: 
                    gamewindow[key].append([(x,y),(x2,y2)])
                
            dispplaythemove(position,x,y,x2,y2)
            previouschnce = [x,y,x2,y2]
            player = position.getplayer()
            position.addtoHistory(position)
            HMC = position.getHMC()
            if HMC>=100 or isStalemate(position) or position.checkRepition():
                checkfordraw = True
                gamefinished = True
            if CheckCHKMTE(position,'white'):
                winner = 'b'
                gamefinished = True
            if CheckCHKMTE(position,'black'):
                winner = 'w'
                gamefinished = True
            if aiChoice and not gamefinished:
                if player==0:
                    colorsign = 1
                else:
                    colorsign = -1
                bestMoveReturn = []
                move_thread = threading.Thread(target = generateNewMove,
                            args = (position,3,-1000000,1000000,colorsign,bestMoveReturn))
                move_thread.start()
                gameprocessing = True
            dragPiece.updatecordinates((x2,y2))

            if not gettransition:
                whiteItemList,blackItemList = renderItem(chessbrd)
            else:
                movingPiece = dragPiece
                origin = getpixel((x,y))
                destiny = getpixel((x2,y2))
                movingPiece.updatepositions(origin)
                step = (destiny[0]-origin[0],destiny[1]-origin[1])

            impo1function([])

    if gettransition:
        p,q = movingPiece.retrivepositions()
        dx2,dy2 = destiny
        n= 30.0
        if abs(p-dx2)<=abs(step[0]/n) and abs(q-dy2)<=abs(step[1]/n):
            movingPiece.updatepositions((-1,-1))
            whiteItemList,blackItemList = renderItem(chessbrd)
            gettransition = False
            impo1function([])
            
        else:
            movingPiece.updatepositions((p+step[0]/n,q+step[1]/n))
    if downward:
        m,k = pygame.mouse.get_pos()
        dragPiece.updatepositions((m-widthofsquare/2,k-heightofsquare/2))

    if gameprocessing and not gettransition:
        if not move_thread.isAlive():
            gameprocessing = False
            impo1function([])
            [x,y],[x2,y2] = bestMoveReturn
            dispplaythemove(position,x,y,x2,y2)
            previouschnce = [x,y,x2,y2]
            player = position.getplayer()
            HMC = position.getHMC()
            position.addtoHistory(position)
            if HMC>=100 or isStalemate(position) or position.checkRepition():
                checkfordraw = True
                gamefinished = True
            if CheckCHKMTE(position,'white'):
                winner = 'b'
                gamefinished = True
            if CheckCHKMTE(position,'black'):
                winner = 'w'
                gamefinished = True
            gettransition = True
            movingPiece = itemInfo((x,y))
            origin = getpixel((x,y))
            destiny = getpixel((x2,y2))
            movingPiece.updatepositions(origin)
            step = (destiny[0]-origin[0],destiny[1]-origin[1])

    renderMaze()
    pygame.display.update()

    clock.tick(60)

pygame.quit()

if gamerecord:
    file_handle.seek(0)
    pickle.dump(gamewindow,file_handle)
    file_handle.truncate()
    file_handle.close()
    
    
    
    
    
    
    
    
    
#This code has been inspred from
#https://github.com/mnahinkhan/Chess/tree/master/Chess