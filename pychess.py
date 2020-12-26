import sys
import chess
import chess.svg
import time
import threading
import math
from random import randint
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget
from weights import Weights

class MoveProbability:
  def __init__(self, move, probability):
    self.move = move
    self.probability = probability 

class AutoChess(QWidget):
  def __init__(self):
    super().__init__()
    self.XSquares = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    self.YSquares = [1, 2, 3, 4, 5, 6, 7, 8]
    self.widgetHeightAndWidth = 800
    self.padding = 30
    self.squareHeightAndWidth = (self.widgetHeightAndWidth - self.padding) / 8
    self.board = chess.Board()
    self.setWindowTitle('Auto Chess')
    self.widgetSvg = QSvgWidget(parent=self)
    self.widgetSvg.setGeometry(0, 0, self.widgetHeightAndWidth, self.widgetHeightAndWidth)
    self.widgetSvg.load(chess.svg.board(self.board).encode('UTF-8'))
    self.show()

  @pyqtSlot(QWidget)
  def mousePressEvent(self, event):
    print('clicked on: ' + self.getXSquare(event.x()))

  @pyqtSlot(QWidget)
  def mouseReleaseEvent(self, event):
    if self.clickIsOnBoard(event.x(), event.y()):
      print('released on board')

  def clickIsOnBoard(self, x, y):
    return (x > self.padding
      and x < self.widgetHeightAndWidth - self.padding
      and y > self.padding
      and y < self.widgetHeightAndWidth - self.padding)

  def getXSquare(self, x):
    squareStart = self.padding
    for xSquare in self.XSquares:
      squareEnd = squareStart + self.squareHeightAndWidth
      if x >= squareStart and x <= squareEnd:
        print(str(x))
        print('square ' + xSquare + ' start: ' + str(squareStart) + ' end: ' + str(squareEnd))
        print('gap: ' + str(squareEnd - squareStart))
        return xSquare
      squareStart = squareEnd
    return 'None'

  def refresh(self):
    self.widgetSvg.load(chess.svg.board(self.board).encode('UTF-8'))

  def auto(self):
    while not self.board.is_game_over():
      self.calculateNextMove()
    else:
      print('Result: ' + self.board.result())
      self.board.reset()
      self.refresh()
      self.auto()
  
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
    
    moveProbabilities.sort(key=lambda x: x.probability, reverse=True)
    return moveProbabilities[0].move

  def calculateMoveProbability(self, piece, move):
    strength = self.getStrength(piece)
    if move.drop:
      return 1
    elif move.promotion:
      return .9
      
    return (randint(0, 100) / 100) / (strength / 100)

  def getStrength(self, piece):
    pieceName = chess.piece_name(piece.piece_type)
    return Weights[pieceName].value
    
  def think(self):
    time.sleep(.25)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  autoChess = AutoChess()
  gameThread = threading.Thread(target=autoChess.auto)
  gameThread.start()
  app.exec_()
