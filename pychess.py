import sys
import chess
import chess.svg
import time
import threading
import math
import numpy as np
from random import randint
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget
from weights import Weights

class MoveProbability:
  def __init__(self, move, probability):
    self.move = move
    self.probability = probability

class PyChess(QWidget):
  def __init__(self):
    super().__init__()
    self.lastClickedSquare = None
    self.positionCount = 0
    self.minimaxDepth = 2
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
      if move in self.getLegalMoves():
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
      if self.board.is_game_over():
        print('Result: ' + self.board.result())
        return
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

  def testMove(self, move):
    self.board.push(move)
  
  def undo(self):
    self.board.pop()

  def calculateNextMove(self):
    self.positionCount = 0
    isMaximisingPlayer = self.board.turn == chess.BLACK
    move = self.getBestLegalMove(self.minimaxDepth, isMaximisingPlayer)
    if move is None:
      move = self.getRandomLegalMove()
    print(self.currentColor() + ' evaluated ' + str(self.positionCount) + ' board positions')
    self.move(move)

  def getRandomLegalMove(self):
    print('Getting a ramdom move for ' + self.currentColor())
    return list(self.getLegalMoves)[randint(0, self.board.legal_moves.count() - 1)]

  def getBestLegalMove(self, depth, isMaximisingPlayer):
    bestMove = None
    bestValue = -9999 if isMaximisingPlayer else 9999
    for move in self.getLegalMoves():
      self.testMove(move)
      boardValue = self.minimax(depth - 1, not isMaximisingPlayer, -10000, 10000)
      self.undo()

      if isMaximisingPlayer:
        if boardValue >= bestValue:
          bestValue = boardValue
          bestMove = move
      else:
          if boardValue <= bestValue:
            bestValue = boardValue
            bestMove = move

    return bestMove

  def getLegalMoves(self):
    return np.concatenate((np.array(list(self.board.legal_moves)), np.array(list(self.board.pseudo_legal_moves))))

  def minimax(self, depth, isMaximisingPlayer, alpha, beta):
    self.positionCount += 1
    if depth == 0:
      return -self.getBoardValue() if isMaximisingPlayer else self.getBoardValue()

    bestValue = -9999 if isMaximisingPlayer else 9999
    for move in self.getLegalMoves():
      self.testMove(move)
      moveValue = self.minimax(depth - 1, not isMaximisingPlayer, alpha, beta)
      self.undo()

      if isMaximisingPlayer:
        bestValue = max(bestValue, moveValue)
        alpha = max(alpha, bestValue)
      else:
        bestValue = min(bestValue, moveValue)
        beta = min(beta, bestValue)

      if beta <= alpha:
        return bestValue

    return bestValue

  def getPieceStrength(self, piece):
    if piece is None:
      return 0
      
    pieceName = chess.piece_name(piece.piece_type)
    return Weights[pieceName].value

  def getBoardValue(self):
    totalValue = 0
    for square in range(0, 64):
      totalValue += self.getPieceStrength(self.board.piece_at(square))
    return totalValue
    
  def think(self):
    time.sleep(.25)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  pyChess = PyChess()
  # gameThread = threading.Thread(target=pyChess.autoPlay)
  # gameThread.start()
  app.exec_()
