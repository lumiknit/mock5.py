#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mock5 analysis

Author: lumiknit (aasr4r4@gmail.com)

Analysis tool for Mock5.

The purpose of this module is:
  * Find game is finished
  * Find out double-3, double-4, 3-4, over-5-stones-in-a-row
"""

#-- Analysis class

class Mock5Analysis:
  """ Omok Anlyzer

  It takes a game board Mock5 and anlayze the state:
  - (TODO) (semi-)opend 4 connections
  - (TODO) 3-3, 3-4, 4-4 after one move
  """

  def __init__(self, game):
    if type(game) is not Mock5: raise TypeError
    self.game = game
    self.run_analysis()

  def run_analysis(): pass

