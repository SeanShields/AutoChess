import sys
import chess
import chess.svg
import time
import threading
import math
import numpy as np
from random import randint
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget
from weights import Weights
from stopwatch import Stopwatch

class MoveProbability:
    def __init__(self, move, probability):
        self.move = move
        self.probability = probability


class PyChess(QWidget):
    def __init__(self):
        super().__init__()
        self.lastClickedSquare = None
        self.positionCount = 0
        self.isPlayerTurn = True
        self.minimaxDepth = 3
        self.XSquares = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.YSquares = [8, 7, 6, 5, 4, 3, 2, 1]
        self.widgetHeightAndWidth = 800
        self.padding = 30
        self.squareHeightAndWidth = (
            self.widgetHeightAndWidth - self.padding * 2) / 8
        self.board = chess.Board()
        self.setWindowTitle('PyChess')
        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(
            0, 0, self.widgetHeightAndWidth, self.widgetHeightAndWidth)
        self.widgetSvg.load(chess.svg.board(self.board).encode('UTF-8'))
        self.show()

    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        if not self.isPlayerTurn:
            return
        
        x = self.getXSquare(event.x())
        y = self.getYSquare(event.y())
        if y is None or x is None:
            return
        
        self.lastClickedSquare = x + str(y)
        square = chess.parse_square(self.lastClickedSquare)
        piece = self.board.piece_at(square)
        if piece is None:
            return
        
        # svg = chess.svg.piece(piece)
        super().setCursor(QtGui.QCursor(Qt.ClosedHandCursor))

    @pyqtSlot(QWidget)
    def mouseReleaseEvent(self, event):
        super().setCursor(QtGui.QCursor(Qt.ArrowCursor))

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
            if self.isPromotable(move):
                move.promotion = 5 # promote to queen
                self.move(move)
            elif self.isMoveLegal(move):
                self.move(move)
            else:
                return

            self.isPlayerTurn = False
            cpuMove = threading.Thread(target=self.calculateNextMove)
            cpuMove.start()
            self.lastClickedSquare = None

    def isMoveLegal(self, move):
        return move in self.board.legal_moves

    def isPromotable(self, move):
        piece = self.board.piece_at(move.from_square)
        if piece is None:
            return False

        name = chess.piece_name(piece.piece_type)
        return name == 'pawn' and (move.to_square in range(0, 9) or move.to_square in range(56, 65))

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

    def testMove(self, move):
        self.board.push(move)

    def undo(self):
        self.board.pop()

    def calculateNextMove(self):
        stopwatch = Stopwatch()
        stopwatch.start()

        self.positionCount = 0
        isMaximisingPlayer = self.board.turn == chess.BLACK
        move = self.getBestLegalMove(self.minimaxDepth, isMaximisingPlayer)
        if move is None:
            print('Result: ' + self.board.result())
            return

        print(self.currentColor() + ' evaluated ' + str(self.positionCount) +
              ' moves in ' + str(round(stopwatch.duration, 2)) + ' seconds')
        stopwatch.reset()
        self.move(move)
        self.isPlayerTurn = True

    def getRandomLegalMove(self):
        print('Getting a ramdom move for ' + self.currentColor())
        return list(self.getLegalMoves())[randint(0, self.board.legal_moves.count() - 1)]

    def getBestLegalMove(self, depth, isMaximisingPlayer):
        bestMove = None
        bestValue = -9999 if isMaximisingPlayer else 9999
        for move in self.board.legal_moves:
            self.testMove(move)
            boardValue = self.minimax(
                depth - 1, not isMaximisingPlayer, -100000, 100000)
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
            moveValue = self.minimax(
                depth - 1, not isMaximisingPlayer, alpha, beta)
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

    def getPieceStrength(self, piece, square):
        if piece is None:
            return 0

        pieceName = chess.piece_name(piece.piece_type)
        return Weights[pieceName].value + self.getSquareWeightForPiece(pieceName, square)

    def getSquareWeightForPiece(self, piece, square):
        weights = []
        if piece == 'pawn':
            weights = [0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, -20, -20, 10, 10, 5,
                5, -5, -10,  0, 0, -10, -5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, 5, 10, 25, 25, 10, 5, 5,
                10, 10, 20, 30, 30, 20, 10, 10,
                50, 50, 50, 50, 50, 50, 50, 50,
                0,  0,  0,  0,  0,  0,  0,  0]
        elif piece == 'knight':
            weights = [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20,  0,  5,  5,  0, -20, -40,
                -30,  5, 10, 15, 15, 10,  5, -30,
                -30,  0, 15, 20, 20, 15,  0, -30,
                -30,  5, 15, 20, 20, 15,  5, -30, -30,
                0, 10, 15, 15, 10,  0, -30, -40,
                -20, 0,  0,  0,  0, -20, -40, -50,
                -40, -30, -30, -30, -30, -40, -50]
        elif piece == 'bishop':
            weights = [
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10,  5,  0,  0,  0,  0,  5, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10,  0, 10, 10, 10, 10,  0, -10,
                -10,  5,  5, 10, 10,  5,  5, -10,
                -10,  0,  5, 10, 10,  5,  0, -10,
                -10,  0,  0,  0,  0,  0,  0, -10,
                -20, -10, -10, -10, -10, -10, -10, -20]
        elif piece == 'rook':
            weights = [
                    0,  0,  0,  5,  5,  0,  0,  0,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    5, 10, 10, 10, 10, 10, 10,  5,
                    0,  0,  0,  0,  0,  0,  0,  0]
        elif piece == 'queen':
            weights = [
                    -20, -10, -10, -5, -5, -10, -10, -20,
                    -10,  0,  5,  0,  0,  0,  0, -10,
                    -10,  5,  5,  5,  5,  5,  0, -10,
                    0,  0,  5,  5,  5,  5,  0, -5,
                    -5,  0,  5,  5,  5,  5,  0, -5,
                    -10,  0,  5,  5,  5,  5,  0, -10,
                    -10,  0,  0,  0,  0,  0,  0, -10,
                    -20, -10, -10, -5, -5, -10, -10, -20]
        elif piece == 'king':
            if self.isLateGame():
                print('late')
                weights = [
                    -50,-30,-30,-30,-30,-30,-30,-50,
                    -30,-30,  0,  0,  0,  0,-30,-30,
                    -30,-10, 20, 30, 30, 20,-10,-30,
                    -30,-10, 30, 40, 40, 30,-10,-30,
                    -30,-10, 30, 40, 40, 30,-10,-30,
                    -30,-10, 20, 30, 30, 20,-10,-30,
                    -30,-20,-10,  0,  0,-10,-20,-30,
                    -50,-40,-30,-20,-20,-30,-40,-50]
            else:
                weights = [
                        20, 30, 10,  0,  0, 10, 30, 20,
                        20, 20,  0,  0,  0,  0, 20, 20,
                        -10, -20, -20, -20, -20, -20, -20, -10,
                        -20, -30, -30, -40, -40, -30, -30, -20,
                        -30, -40, -40, -50, -50, -40, -40, -30,
                        -30, -40, -40, -50, -50, -40, -40, -30,
                        -30, -40, -40, -50, -50, -40, -40, -30,
                        -30, -40, -40, -50, -50, -40, -40, -30]

        if self.board.turn == chess.BLACK:
            return list(reversed(weights))[square]
        else:
            return weights[square]

    def isLateGame(self):
        # TODO: fix this
        queenCount = 0
        for square in range(0, 64):
            piece = self.board.piece_at(square)
            if piece is None:
                continue

            if piece.piece_type == 5:
                queenCount += 1

        return queenCount == 0

    def getBoardValue(self):
        totalValue = 0
        for square in range(0, 64):
            totalValue += self.getPieceStrength(self.board.piece_at(square), square)
        return totalValue

    def think(self):
        time.sleep(.25)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pyChess = PyChess()
    # gameThread = threading.Thread(target=pyChess.autoPlay)
    # gameThread.start()
    app.exec_()
