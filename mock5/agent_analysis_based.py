#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mock5 agent: strategy = analysis based greedy

Author: lumiknit (aasr4r4@gmail.com)

Guess scores from analysis and pick max score.

Use `agent` function.

"""

from mock5.analysis import *

def score_at(game, a, i):
  import math
  import random
  score = 1
  r, c = game._expand_index(i)
  if game[r, c] != 0: return 0
  hh = (game.height - 1) / 2
  hw = (game.width - 1) / 2
  dr, dc = r - hh, c - hw
  # Center is preffered
  score += math.sqrt(hh * hh + hw * hw) - math.sqrt((dr * dr) + (dc * dc))
  # Make some noise for random choice
  score += random.random()
  for dir in range(4):
    m = a.get_critical_at(game.player, dir, i)
    o = a.get_critical_at(3 - game.player, dir, i)
    score += (10 ** m) + (10 ** o) * 0.7
  return score

def policy(game):
  import numpy as np
  a = Analysis(game)
  scores = np.zeros(game.height * game.width)
  for i in range(game.height * game.width):
    scores[i] = score_at(game, a, i)
  return scores
policy.name = "greedy"

def agent(game):
  a = Analysis(game)

  max_s = -float('inf')
  max_i = None

  for i in range(game.height * game.width):
    score = score_at(game, a, i)
    if score > max_s: max_s, max_i = score, i
  if max_i is None: return None
  return game._expand_index(max_i)

agent.name = "agent-analysis-based"
