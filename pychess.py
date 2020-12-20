import sys
import chess
import chess.svg
import time
import threading
from random import randint
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget

class MoveProbability:
  def __init__(self, move, probability):
    self.move = move
    self.probability = probability 

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
      print('Result: ' + self.board.result())
  
  def currentColor(self):
    return 'White' if self.board.turn == chess.WHITE else 'Black'

  def move(self, move):
    self.board.push(move)
    self.refresh()

  def calculateNextMove(self):
    self.think()
    move = self.getBestLegalMove()
    if move in self.board.legal_moves:
      self.move(move)
    else:
     print('Invalid move')

  def getRamdomLegalMove(self):
    print('Getting a ramdom move for ' + self.currentColor())
    return list(self.board.legal_moves)[randint(0, self.board.legal_moves.count() - 1)]

  def getBestLegalMove(self):
    moveProbabilities = []
    for move in list(self.board.legal_moves):
      probability = self.calculateMoveProbability(self.board.piece_at(move.from_square), move)
      if probability > 0:
        moveProbabilities.append(MoveProbability(move, probability))
    
    if len(moveProbabilities) > 0:
      moveProbabilities.sort(key=lambda x: x.probability, reverse=True)
      return moveProbabilities[0].move

    return self.getRamdomLegalMove()

  def calculateMoveProbability(self, peice, move):
    probability = randint(0, 100) / 100
    return probability

  def think(self):
    time.sleep(.25)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  autoChess = AutoChess()
  gameThread = threading.Thread(target=autoChess.start)
  gameThread.start()
  app.exec_()
