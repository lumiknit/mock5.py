#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mock5 agent: strategy = analysis based greedy

Author: lumiknit (aasr4r4@gmail.com)

Guess scores from analysis and pick max score.

Use `agent` function.

"""

from mock5.analysis import *

def agent(game):
  import math
  import random

  a = Analysis(game)

  my = game.player
  op = 3 - game.player

  max_s = -float('inf')
  max_i = None

  score = [0] * (game.height * game.width)
  for i in range(game.height * game.width):
    r, c = game._expand_index(i)
    if game[r, c] != 0: continue
    dr = r - game.height / 2
    dc = c - game.width / 2
    # Center is preffered
    score[i] -= math.sqrt((dr * dr) + (dc * dc))
    # Make some noise for random choice
    score[i] += random.random()
    for dir in range(4):
      m = a.get_critical_at(my, dir, i)
      o = a.get_critical_at(op, dir, i)
      score[i] += (10 ** m) + (10 ** o) * 0.7
    if score[i] > max_s:
      max_s = score[i]
      max_i = i
  if max_i is None: return None
  return game._expand_index(max_i)

agent.name = "agent-analysis-based"
