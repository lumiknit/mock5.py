#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Play mock5

Author: lumiknit (aasr4r4@gmail.com)

Simple Omok (five-in-a-row) game for RL with numpy/torch.

Example:
  # For playing game with to user, run this script such as:
  ./play.py [<AGENT_TYPE>] [<BOARD_HEIGHT> <BOARD_WIDTH>]
  # for example,
  ./play.py
  ./play.py random        # play with agent-random
  ./play.py 11 12         # play in 11x12 board
  ./play.py silly 14 14   # play in 14x14 board with agent-silly
"""

from mock5 import Mock5

#-- Entrypoint

if __name__ == "__main__":
  import sys
  import mock5.agent_random
  import mock5.agent_analysis_based
  agents = {}
  agents["random"] = mock5.agent_random.agent
  agents["silly"] = mock5.agent_analysis_based.agent
  g = None
  l = len(sys.argv)
  if l <= 1:
    Mock5().play()
  elif l == 2:
    Mock5().play(agents[sys.argv[1]])
  elif l == 3:
    h = int(sys.argv[1])
    w = int(sys.argv[2])
    Mock5(h, w).play()
  else:
    h = int(sys.argv[2])
    w = int(sys.argv[3])
    Mock5().play(agents[sys.argv[1]])
