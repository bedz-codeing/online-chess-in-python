from pieces import *
class Board():
    def __init__(self):
        self.board = self.create_board()
    def create_board(self):
        board = []
        for i in range(8):
            row = []
            for j in range(8):
                row.append("")
            board.append(row)
        return board
    def load_FEN(self,fen):
        row = 0
        column = 0
        for i in fen :
            #what is the diff here if i use ifs insted of elifs
            if  i == "r":
                    pass
            elif  i == "b":
                    pass
                    column+=1 
            elif  i == "n":
                    pass
                    column+=1
            elif  i == "q":
                    self.board[column][row] = queen("black",column,row,"chess pieces/black_queen.png")
                    column+=1 
            elif  i == "k":
                    self.board[column][row] = king("black",column,row,"chess pieces/black_king.png")
                    column+=1
            elif  i == "p":
                    self.board[column][row]=pawn("black",column,row,"chess pieces/black_pawn.png")
                    column+=1     
            elif i =="/":
                row +=1
                column =0
            elif i.isnumeric():
                column += int(i)
            elif  i == "R":
                    pass
                    column+=1
            elif  i == "B":
                    pass
                    column+=1
            elif  i == "N":
                    pass
                    column+=1
            elif  i == "Q":
                    self.board[column][row] = queen("white",column,row,"chess pieces/white_qween.png")
                    column+=1
            elif  i == "K":
                    self.board[column][row] = king("white",column,row,"chess pieces/white_king.png")
                    column+=1
            elif  i == "P":
                    white_pawn =pawn("white",column,row,"chess pieces/white_pawn.png")
                    white_pawn.load_image()
                    white_pawn.draw_piece()
                    column+=1     