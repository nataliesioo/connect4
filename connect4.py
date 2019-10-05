#https://github.com/KeithGalli/Connect4-Python/blob/master/connect4.py

import numpy as np
import random
import pygame
import sys
import math
import time ####

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

MINIMAX_DEPTH = 8 ####

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

PAD_LEN = 2 ####

WINDOW_LENGTH = 5

R2R3_WINDOW_LENGTH = 4 # rule2,3 window length 
R5_WINDOW_LENGTH = 3 # rule5 window length 

def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0


def firstmove_violation(col, first): ###fmv###
    if first>0 and col==3:
        return 1
    else:
        return 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

#check if it's a winning move when opponent put on the column that was put
def col_winning_move(board, piece, col): #####
	op = PLAYER_PIECE #opponent piece
	if piece == PLAYER_PIECE:
		op = AI_PIECE
	# Check horizontal locations for win
	if is_valid_location(board,col)==0:
	    return False
	row=get_next_open_row(board,col)
	nboard=board.copy()
	nboard[row][col]=op

	if is_valid_location(board,col)==0:
	    return False
	row=get_next_open_row(board,col)
	nboard[row][col]=piece #put a opponent piece on the column that was put

	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if nboard[r][c] == piece and nboard[r][c+1] == piece and nboard[r][c+2] == piece and nboard[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if nboard[r][c] == piece and nboard[r+1][c] == piece and nboard[r+2][c] == piece and nboard[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if nboard[r][c] == piece and nboard[r+1][c+1] == piece and nboard[r+2][c+2] == piece and nboard[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if nboard[r][c] == piece and nboard[r-1][c+1] == piece and nboard[r-2][c+2] == piece and nboard[r-3][c+3] == piece:
				return True
	return False

def evaluate_window(window, p): #####
	score = 0
	op = PLAYER_PIECE #opponent piece
	if p == PLAYER_PIECE:
		op = AI_PIECE

	if window[0:4]==[p,p,p,p] or window[1:5]==[p,p,p,p]: #4 in a row
	    score += 100
	elif window[0:4]==[0,p,p,p] or window[1:5]==[p,p,p,0]: #3 in a row (possible 4 in a row)
	    score += 8
	    #score += 1
	elif window[0:3]==[0,p,p] or window[2:5]==[p,p,0]: #2 in a row (possible 3 in a row)
	    score += 4
	    #score += 1
	elif window[0:3]==[0,0,p] or window[2:5]==[p,0,0]: #possible 2 in a row
	    score += 2

	return score

def op_evaluate_window(window, p): #####
	score = 0
	op = PLAYER_PIECE #opponent piece
	if p == PLAYER_PIECE:
		op = AI_PIECE

	if window[0:4]==[0,op,op,op] or window[1:5]==[op,op,op,0]: #opponent 3 in a row
	    score += -3
	    #score += -1
	elif window[0:3]==[0,op,op] or window[2:5]==[op,op,0]: #opponent 2 in a row
	    score += -1

	return score


def heuristic(board, piece): ## evaluate the heuristic value of a given board
	score = 0
	op = PLAYER_PIECE #opponent piece
	if piece == PLAYER_PIECE:
		op = AI_PIECE

	for i in range(ROW_COUNT): #copying board elements into the padded board
	    padded_board[i+PAD_LEN][PAD_LEN:COLUMN_COUNT+PAD_LEN] = list(board.astype(int)[i][:])

	for r in range(PAD_LEN,ROW_COUNT+PAD_LEN,1):
		for c in range(PAD_LEN,COLUMN_COUNT+PAD_LEN,1):
		    if padded_board[r][c] == piece:
		        pdwindow = [padded_board[r-2+i][c-2+i] for i in range(WINDOW_LENGTH)] ## posiive sloped diagonal
		        ndwindow = [padded_board[r+2-i][c-2+i] for i in range(WINDOW_LENGTH)] ## negative sloped diagonal
		        vwindow = [padded_board[r-2+i][c] for i in range(WINDOW_LENGTH)] ## vertical
		        hwindow = [padded_board[r][c-2+i] for i in range(WINDOW_LENGTH)] ## horizontal
		        score+=evaluate_window(pdwindow,piece)+evaluate_window(ndwindow,piece)+evaluate_window(vwindow,piece)+evaluate_window(hwindow,piece)
		    if padded_board[r][c] == op:
		        pdwindow = [padded_board[r-2+i][c-2+i] for i in range(WINDOW_LENGTH)] ## posiive sloped diagonal
		        ndwindow = [padded_board[r+2-i][c-2+i] for i in range(WINDOW_LENGTH)] ## negative sloped diagonal
		        vwindow = [padded_board[r-2+i][c] for i in range(WINDOW_LENGTH)] ## vertical
		        hwindow = [padded_board[r][c-2+i] for i in range(WINDOW_LENGTH)] ## horizontal
		        score+=op_evaluate_window(pdwindow,piece)+op_evaluate_window(ndwindow,piece)+op_evaluate_window(vwindow,piece)+op_evaluate_window(hwindow,piece)
	return score

def is_terminal_node(board):
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

#returns column, -1 when fail
def rule1(first_move, first_turn):
    col=0
    if first_turn==1 and first_move==1: #
        col=3
    elif first_turn==0 and first_move==1: #
        col=4
    return col-1

def is_valid_location_padded_board(padded_board, col):
	return padded_board[PAD_LEN+ROW_COUNT-1][col] == 0

def get_next_open_row_padded_board(padded_board, col):
	for r in range(PAD_LEN,ROW_COUNT+PAD_LEN,1):
		if padded_board[r][col] == 0:
			return r

#if currently 3 in a row, and 4 in a row possible, return the index of window, otherwise -1
def rule2_check(window, piece):
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 3 and window.count(EMPTY) == 1:
	    return window.index(EMPTY)
	return -1

#return a column to win. -1 if not found
def rule2(board, piece):
	# Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+R2R3_WINDOW_LENGTH]
			offset=rule2_check(window,piece)
			if offset != -1:
			    if is_valid_location(board,c+offset)==1 and get_next_open_row(board,c+offset)==r:
			        return c+offset

	# Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+R2R3_WINDOW_LENGTH]
			offset=rule2_check(window,piece)
			if offset != -1:
			    if is_valid_location(board,c)==1 and get_next_open_row(board,c)==r+offset:
			        return c

	# posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(R2R3_WINDOW_LENGTH)]
			offset=rule2_check(window,piece)
			if offset != -1:
			    if is_valid_location(board,c+offset)==1 and get_next_open_row(board,c+offset)==r+offset:
			        return c+offset

    # negative sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(R2R3_WINDOW_LENGTH)]
			offset=rule2_check(window,piece) 
			if offset != -1: #(r+3-offset,c+offset)
			    if is_valid_location(board,c+offset)==1 and get_next_open_row(board,c+offset)==r+3-offset:
			        return c+offset
	return -1

#if currently opponent 3 in a row, and 4 in a row possible, return the index of window, otherwise -1
def rule3_check(window, piece):
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
	    return window.index(EMPTY)
	return -1

#return a column to block. -1 if not found
def rule3(board, piece):
	# Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+R2R3_WINDOW_LENGTH]
			offset=rule3_check(window,piece)
			if offset != -1:
			    if is_valid_location(board,c+offset)==1 and get_next_open_row(board,c+offset)==r:
			        return c+offset

	# Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+R2R3_WINDOW_LENGTH]
			offset=rule3_check(window,piece)
			if offset != -1:
			    if is_valid_location(board,c)==1 and get_next_open_row(board,c)==r+offset:
			        return c

	# posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(R2R3_WINDOW_LENGTH)]
			offset=rule3_check(window,piece)
			if offset != -1:
			    if is_valid_location(board,c+offset)==1 and get_next_open_row(board,c+offset)==r+offset:
			        return c+offset

    # negative sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(R2R3_WINDOW_LENGTH)]
			offset=rule3_check(window,piece) 
			if offset != -1: #(r+3-offset,c+offset)
			    if is_valid_location(board,c+offset)==1 and get_next_open_row(board,c+offset)==r+3-offset:
			        return c+offset
	return -1


#return 0 if not found, -1 if front to block, 1 if back to block
def rule4_window_check(window, p):
    op = PLAYER_PIECE #opponent piece
    if p == PLAYER_PIECE:
        op = AI_PIECE
    if window==[0,op,op,0,0]:
        return 1
    if window==[0,0,op,op,0]:
        return -1
    return 0

#return -1 when not found, column otherwise
def rule4(board, piece):
	for i in range(ROW_COUNT): #copying board elements into the padded board
	    padded_board[i+PAD_LEN][PAD_LEN:COLUMN_COUNT+PAD_LEN] = list(board.astype(int)[i][:])
	op = PLAYER_PIECE #opponent piece
	if piece == PLAYER_PIECE:
	    op = AI_PIECE
	for r in range(PAD_LEN,ROW_COUNT+PAD_LEN,1):
		for c in range(PAD_LEN,COLUMN_COUNT+PAD_LEN,1):
		    if padded_board[r][c] == op:
		        pdwindow = [padded_board[r-2+i][c-2+i] for i in range(WINDOW_LENGTH)] ## posiive sloped diagonal
		        ndwindow = [padded_board[r+2-i][c-2+i] for i in range(WINDOW_LENGTH)] ## negative sloped diagonal
		        hwindow = [padded_board[r][c-2+i] for i in range(WINDOW_LENGTH)] ## horizontal
		        ch = rule4_window_check(pdwindow,piece)
		        if ch == -1:
		            if is_valid_location(padded_board,c-1)==1 and get_next_open_row_padded_board(padded_board,c-1)==r-1:
		                if col_winning_move(board,op,c-1-PAD_LEN)==False:
		                    return c-1-PAD_LEN
		        elif ch == 1:
		            if is_valid_location(padded_board,c+1)==1 and get_next_open_row_padded_board(padded_board,c+1)==r+1:
		                if col_winning_move(board,op,c+1-PAD_LEN)==False:
		                    return c+1-PAD_LEN
		        ch = rule4_window_check(ndwindow,piece)
		        if ch == -1: #(r+1,c-1)
		            if is_valid_location(padded_board,c-1)==1 and get_next_open_row_padded_board(padded_board,c-1)==r+1:
		                if col_winning_move(board,op,c-1-PAD_LEN)==False:
		                    return c-1-PAD_LEN
		        elif ch == 1: #(r-1,c+1)
		            if is_valid_location(padded_board,c+1)==1 and get_next_open_row_padded_board(padded_board,c+1)==r-1:
		                if col_winning_move(board,op,c+1-PAD_LEN)==False:
		                    return c+1-PAD_LEN
		        ch = rule4_window_check(hwindow,piece)
		        if ch == -1:
		            if is_valid_location(padded_board,c-1)==1 and get_next_open_row_padded_board(padded_board,c-1)==r:
		                if col_winning_move(board,op,c-1-PAD_LEN)==False:
		                    return c-1-PAD_LEN
		        elif ch == 1:
		            if is_valid_location(padded_board,c+1)==1 and get_next_open_row_padded_board(padded_board,c+1)==r:
		                if col_winning_move(board,op,c+1-PAD_LEN)==False:
		                    return c+1-PAD_LEN
	return -1


#return -1 when fail, column when found
def rule5(board, piece):
	for i in range(ROW_COUNT): #copying board elements into the padded board
	    padded_board[i+PAD_LEN][PAD_LEN:COLUMN_COUNT+PAD_LEN] = list(board.astype(int)[i][:])
	op = PLAYER_PIECE # opponent piece
	if piece == PLAYER_PIECE:
		op = AI_PIECE
	for r in range(PAD_LEN,ROW_COUNT+PAD_LEN,1):
		for c in range(PAD_LEN,COLUMN_COUNT+PAD_LEN,1):
		    if padded_board[r][c] == EMPTY and is_valid_location_padded_board(padded_board,c) ==1 and get_next_open_row_padded_board(padded_board,c)==r:
		        ews=[] #Windows with (r,c) in the End
                ## posiive sloped diagonals
		        ews.append([padded_board[r+i][c+i] for i in range(R5_WINDOW_LENGTH)])
		        ews.append([padded_board[r-i][c-i] for i in range(R5_WINDOW_LENGTH)])

		        ## negative sloped diagonals
		        ews.append([padded_board[r+i][c-i] for i in range(R5_WINDOW_LENGTH)])
		        ews.append([padded_board[r-i][c+i] for i in range(R5_WINDOW_LENGTH)])
		        

                ## horizontal
		        ews.append([padded_board[r][c-i] for i in range(R5_WINDOW_LENGTH)])
		        ews.append([padded_board[r][c+i] for i in range(R5_WINDOW_LENGTH)])

                ## vertical
		        ews.append([padded_board[r-i][c] for i in range(R5_WINDOW_LENGTH)])

		        cws=[] #Windows with (r,c) in the Center
                ## posiive sloped diagonal
		        cws.append([padded_board[r-1+i][c-1+i] for i in range(R5_WINDOW_LENGTH)])
                ## negative sloped diagonals
		        cws.append([padded_board[r-1+i][c+1-i] for i in range(R5_WINDOW_LENGTH)])
		        ## horizontal
		        cws.append([padded_board[r][c-1+i] for i in range(R5_WINDOW_LENGTH)])

		        sel_ews=[]
		        sel_cws=[]
		        for ew in ews:
		            if ew == [EMPTY,op,op]:
		                sel_ews.append(ew)
		        for cw in cws:
		            if cw == [op,EMPTY,op]:
		                sel_cws.append(cw)
		        cnt=len(sel_ews)+len(sel_cws)

		        for a in sel_ews:
		            for b in sel_cws:
		                if a[0] == b[1]:
		                    cnt-=1
		        if cnt>=2:
		            if col_winning_move(board,op,c-PAD_LEN)==False:
		                return c-PAD_LEN

	return -1


#return -1 when fail, column when found
def rule6(board, piece):
    if is_valid_location(board,COLUMN_COUNT//2) == 1:
        return COLUMN_COUNT//2
    return -1

#return -1 when fail, column when found
def rule7(board, piece,player_col):
    if is_valid_location(board,player_col) == 1:
        return player_col
    return -1

#return (0,-1) when no rule to apply, (rule number,column) otherwise
def apply_rule(board, piece, first_move, first_turn,player_col):
    col=-1
    col=rule1(first_move,first_turn)
    if col != -1:
        return 1,col
    col=rule2(board,piece)
    if col != -1:
        return 2,col
    col=rule3(board,piece)
    if col != -1:
        return 3,col
    col=rule4(board,piece)
    if col != -1:
        return 4,col
    col=rule5(board,piece)
    if col != -1:
        return 5,col
    #col=rule6(board, piece) #####
    #if col != -1:
    #    return 6,col
    #col=rule7(board, piece,player_col) #####
    #if col != -1:
    #    return 7,col
    return 0,col

#returns columns, values, column, value
def minimax(board, depth, alpha, beta, maximizingPlayer):
	columns = [] #
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, AI_PIECE):
				return (None, None, None, 100000000000000) #
			elif winning_move(board, PLAYER_PIECE):
				return (None, None, None, -10000000000000) #
			else: # Game is over, no more valid moves
				return (None, None, None, 0) #
		else: # Depth is zero
			return (None, None, None, heuristic(board, AI_PIECE)) #
	if maximizingPlayer:
		values = [-math.inf,-math.inf,-math.inf,-math.inf,-math.inf,-math.inf,-math.inf] #####
		value = -math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[3] #
			if col not in columns: #
			    columns.append(col) #
			    values[col]=new_score #####
			#else: #####
			if values[col]<new_score: #####
			    values[col]=new_score #####
			
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return columns, values, column, value #

	else: # Minimizing player
		values = [math.inf,math.inf,math.inf,math.inf,math.inf,math.inf,math.inf] #####
		value = math.inf
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[3] #
			if col not in columns: #
			    columns.append(col) #
			    values[col]=new_score #####
			#else: #####
			if values[col]<new_score: #####
			    values[col]=new_score #####
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return columns, values, column, value #

#old_get_valid_locations 
def old_get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

#new_get_valid_locations
def get_valid_locations(board): #####
	valid_locations = []
	if is_valid_location(board, 3):
			valid_locations.append(3)
	if is_valid_location(board, 2):
			valid_locations.append(2)
	if is_valid_location(board, 4):
			valid_locations.append(4)
	if is_valid_location(board, 1):
			valid_locations.append(1)
	if is_valid_location(board, 5):
			valid_locations.append(5)
	if is_valid_location(board, 0):
			valid_locations.append(0)
	if is_valid_location(board, 6):
			valid_locations.append(6)
	return valid_locations

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()

board = create_board()

padded_board = [[3 for x in range(COLUMN_COUNT+(PAD_LEN*2))] for y in range(ROW_COUNT+(PAD_LEN*2))] ###

fboard=board.copy() ###fmv###
fboard[5][3]=AI_PIECE ###fmv###
fboard[0][3]=AI_PIECE ###fmv###

#print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

print("A: AI first, P: player first") ###cf###
for line in sys.stdin:
    stin=line.rstrip()
    if stin=='A':
        turn=AI
    elif stin=='P':
        turn=PLAYER
    else:
        print("Wrong input")
        continue
    break ###cf###
first_turn=turn ### save the first turn

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

firstmove=1 ###fmv###
AIfirstmove=1 ###rul1 and rule 2

player_col=-1#####
while not game_over: ## game loop

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
			#print(event.pos)

			# Ask for Player 1 Input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col) and not firstmove_violation(col,firstmove): ###fmv###
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)
					player_col=col #####

					if winning_move(board, PLAYER_PIECE):
						label = myfont.render("Player wins!!", 1, RED)
						screen.blit(label, (40,10))
						game_over = True

					turn += 1
					turn = turn % 2

					print("Player move") #
					print_board(board)
					draw_board(board)
					firstmove = 0 ###fmv###

	# AI turn
	if turn == AI and not game_over:				

		delta=time.time() ####

		(rule,col) = apply_rule(board, AI_PIECE,AIfirstmove,first_turn, player_col) ### try rule
		if rule==0: ### if no rule to apply, do minimax
		    if firstmove is 1: ###fmv###
		        columns, values, col, minimax_score = minimax(fboard, MINIMAX_DEPTH, -math.inf, math.inf, True) #
		    else:
		       columns, values, col, minimax_score = minimax(board, MINIMAX_DEPTH, -math.inf, math.inf, True) # ###fmv###
		#col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
		delta=time.time()-delta ####

		if col == None: #### when draw
		    label = myfont.render("Draw", 1, YELLOW)
		    screen.blit(label, (40,10))
		    game_over = True
		    draw_board(board)
		    pygame.time.wait(3000)
		    break

		if is_valid_location(board, col)==1 and firstmove_violation(col,firstmove)==0: ###fmv###
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)

			if winning_move(board, AI_PIECE):
				label = myfont.render("AI wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				game_over = True
			
			if rule==0: ### print statement when minimax search applied
			    print("column"," \t","heuristic value") #
			    for i in range(len(columns)): #
			        print(columns[i]+1,"\t:\t",values[columns[i]]) #####
			    print("AI move")
			    print("column with the highest heuristic value : ",col+1,"  heuristic value : ",minimax_score)
			else: ### print statement when rule is applied
			    print("By rule",rule,",","column ",col+1,"is selected\n")


			print("Time :",delta," seconds") ####
			print_board(board)
			print("\n")

			draw_board(board)

			turn += 1  
			turn = turn % 2 ## switch player ##
			firstmove = 0 ###fmv###
			AIfirstmove = 0

	if game_over: ## time delay when game over ##
		pygame.time.wait(3000)
