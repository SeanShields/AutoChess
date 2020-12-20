import sys
import chess
import chess.svg
import time
import threading
from random import randint
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget

class AutoChess(QWidget):
  def __init__(self):
    super().__init__()
    self.board = chess.Board()

    self.setWindowTitle('Auto Chess')
    self.setGeometry(100, 100, 800, 800)
    self.widgetSvg = QSvgWidget(parent=self)
    self.widgetSvg.setGeometry(10, 10, 770, 770)
    self.widgetSvg.load(chess.svg.board(self.board).encode("UTF-8"))
    self.show()
  
  def refresh(self):
    self.widgetSvg.load(chess.svg.board(self.board).encode("UTF-8"))

  def start(self):
    while not self.board.is_game_over():
      self.calculateNextMove()
    else:
      winner = 'White' if self.board.turn == chess.WHITE else 'Black'
      print('Winner: ' + winner)

  def move(self, move):
    self.board.push(move)
    self.refresh()

  def calculateNextMove(self):
    move = self.getWhiteMove() if self.board.turn == chess.WHITE else self.getBlackMove()
    self.think()
    if move in self.board.legal_moves:
      self.move(move)
    else:
     print('invalid move')

  def getWhiteMove(self):
    return self.getRamdomLegalMove()

  def getBlackMove(self):
    return self.getRamdomLegalMove()

  def getRamdomLegalMove(self):
    moves = list(self.board.legal_moves)
    move = moves[randint(0, self.board.legal_moves.count() - 1)]
    return move

  def think(self):
    time.sleep(.25)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  autoChess = AutoChess()
  gameThread = threading.Thread(target=autoChess.start)
  gameThread.start()
  app.exec_()


