# -*- coding: utf-8 -*-
"""mock5/read_record.py

Author: lumiknit (aasr4r4@gmail.com)

Record (generated by gen.cpp) reader for torch
"""
import struct
import torch

class IntPairBytesIter:
  def __init__(self, b):
    self.b = b
    self.i = 0
    self.l = len(b)
    if self.l % 8 != 0:
      raise ValueError

  def __iter__(self): return self

  def __next__(self):
    if self.i >= self.l: raise StopIteration
    i = self.i
    self.i += 8
    return struct.unpack("ii", self.b[i : i + 8])

  def rewind(self):
    self.i = 0

class IntPairArrayIter:
  def __init__(self, a):
    self.a = a
    self.i = 0
    self.l = len(a)
    if self.l % 2 != 0:
      raise ValueError

  def __iter__(self): return self

  def __next__(self):
    if self.i >= self.l: raise StopIteration
    i = self.i
    self.i += 2
    return self.a[i], self.a[i + 1]

  def rewind(self):
    self.i = 0

def int_pair_iter(container):
  if type(container) is Bytes: return IntPairBytesIter(container)
  else: return IntPairArrayIter(container)

def file_to_int_pair_iter(filename):
  with open(filename, "rb") as f:
    return IntPairBytesIter(f.read())

def conv_record(X, Y, w, i2iter, index_map):
  left, v, a = 0, 0, 0
  for i0, i1 in i2iter:
    if left <= 0:
      z = [torch.ones(w, w, dtype=torch.float),
            torch.zeros(w, w, dtype=torch.float),
            torch.zeros(w, w, dtype=torch.float)]
      bd_my = torch.stack(z)
      bd_op = bd_my.clone()
      a = [0, 1, -1][i0]
      v = 1
      left = i1
    else:
      idx, sc = i0, a
      x, y = index_map(idx // w, idx % w)
      bd_my[0][y][x] = 0
      bd_my[v][y][x] = 1
      X.append(bd_my.clone())
      Y.append(torch.tensor([sc], dtype=torch.float))
      bd_op[0][y][x] = 0
      bd_op[3 - v][y][x] = 1
      X.append(bd_op.clone())
      Y.append(torch.tensor([-sc], dtype=torch.float))
      v = 3 - v
      left -= 1


def conv_records(w, i2iter):
  def make_symm(r, f, w):
    def g(y, x):
      x = x if f == 0 else w - 1 - x
      if r == 1: return w - 1 - x, y
      elif r == 2: return w - 1 - y, w - 1 - x
      elif r == 3: return x, w - 1 - y
      else: return y, x
    return g
  X, Y = [], []
  for f in range(2):
    for r in range(4):
      i2iter.rewind()
      conv_record(X, Y, w, i2iter, make_symm(r, f, w))
  Xs = torch.stack(X)
  Ys = torch.stack(Y)
  return Xs, Ys

def conv_records_from_array(w, a):
  return conv_records(w, IntPairArrayIter(a))

def conv_records_from_file(w, filename):
  return conv_records(w, file_to_int_pair_iter(filename))

if __name__ == "__main__":
  x, y = conv_records_from_file(11, "out")
  print(x.shape, y.shape)
  print(x)
  print(y)
