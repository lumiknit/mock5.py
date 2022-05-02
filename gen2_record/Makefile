.phony: all run

CC = /usr/local/opt/llvm/bin/clang++
FLAGS = -L/usr/local/opt/llvm/lib -fopenmp -I/usr/local/opt/llvm/include

all: gen.cpp
	$(CC) -Wall -O2 $(FLAGS) -o gen gen.cpp

run:
	./gen out 100 11 11 0.03
