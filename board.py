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
                   self.board[column][row]=rook("black",column,row,"chess pieces/black_rook.png")
                   column+=1 
            elif  i == "b":
                    self.board[column][row]=bishop("black",column,row,"chess pieces/black_bishop.png")
                    column+=1 
            elif  i == "n":
                    self.board[column][row]=knight("black",column,row,"chess pieces/black_knight.png")
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
                    self.board[column][row]=rook("white",column,row,"chess pieces/white_rook.png")
                    column+=1
            elif  i == "B":
                    self.board[column][row]=bishop("white",column,row,"chess pieces/white_bishop.png")
                    column+=1
            elif  i == "N":
                    self.board[column][row]=knight("white",column,row,"chess pieces/white_knight.png")
                    column+=1
            elif  i == "Q":
                    self.board[column][row] = queen("white",column,row,"chess pieces/white_qween.png")
                    column+=1
            elif  i == "K":
                    self.board[column][row] = king("white",column,row,"chess pieces/white_king.png")
                    column+=1
            elif  i == "P":
                        self.board[column][row]=pawn("white",column,row,"chess pieces/white_pawn.png")
                        column+=1