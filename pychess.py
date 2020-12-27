import sys
import chess
import chess.svg
import time
import threading
import math
from random import randint
import drawSvg as draw
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
    self.lastClickedSquare = None
    self.XSquares = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    self.YSquares = [8, 7, 6, 5, 4, 3, 2, 1]
    self.widgetHeightAndWidth = 800
    self.padding = 30
    self.squareHeightAndWidth = (self.widgetHeightAndWidth - self.padding * 2) / 8
    self.board = chess.Board()
    self.setWindowTitle('Auto Chess')
    self.widgetSvg = QSvgWidget(parent=self)
    self.widgetSvg.setGeometry(0, 0, self.widgetHeightAndWidth, self.widgetHeightAndWidth)
    self.widgetSvg.load(chess.svg.board(self.board).encode('UTF-8'))
    self.show()

  @pyqtSlot(QWidget)
  def mousePressEvent(self, event):
    x = self.getXSquare(event.x())
    y = self.getYSquare(event.y())
    if y is not None and x is not None:
      self.lastClickedSquare = x + str(y)
      # TODO: Draw line/arrow under cursor

  @pyqtSlot(QWidget)
  def mouseReleaseEvent(self, event):
    if self.lastClickedSquare is None:
      return

    x = self.getXSquare(event.x())
    y = self.getYSquare(event.y())
    if x is None or y is None:
      self.lastClickedSquare = None
      return

    releaseSquare = x + str(y)
    if releaseSquare != self.lastClickedSquare:
      move = chess.Move.from_uci(self.lastClickedSquare + x + str(y))
      if move in self.board.legal_moves:
        self.move(move)
        cpuMove = threading.Thread(target=self.calculateNextMove)
        cpuMove.start()
      self.lastClickedSquare = None

  def getXSquare(self, x):
    squareStart = self.padding
    for xSquare in self.XSquares:
      squareEnd = squareStart + self.squareHeightAndWidth
      if x >= squareStart and x <= squareEnd:
        return xSquare
      squareStart = squareEnd
    return None

  def getYSquare(self, y):
    squareStart = self.padding
    for ySquare in self.YSquares:
      squareEnd = squareStart + self.squareHeightAndWidth
      if y >= squareStart and y <= squareEnd:
        return ySquare
      squareStart = squareEnd
    return None

  def refresh(self):
    self.widgetSvg.load(chess.svg.board(self.board).encode('UTF-8'))

  def autoPlay(self):
    while not self.board.is_game_over():
      self.calculateNextMove()
    else:
      print('Result: ' + self.board.result())
      self.board.reset()
      self.refresh()
      self.autoPlay()
  
  def currentColor(self):
    return 'White' if self.board.turn == chess.WHITE else 'Black'

  def move(self, move):
    self.board.push(move)
    self.refresh()

  def calculateNextMove(self):
    if self.board.is_game_over():
      print('Result: ' + self.board.result())
      return

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
    time.sleep(1)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  autoChess = AutoChess()
  # gameThread = threading.Thread(target=autochess.calculateNexMove)
  # gameThread.start()
  app.exec_()
