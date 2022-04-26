/* gen.cpp
 * Omok record generator based on algorithmic moves for ML
 * Author: lumiknit (aasr4r4@gmail.com)
 *
 * The algorithm is based on mock5/analysis and mock5/agent_analysis_based.
 *
 * Compilation: YOU MUST ADD OPTION for OpenMP!
 * e.g. g++ gen.cpp -o gen -fopenmp
 * Usage: ./gen <OUT_FILE_NAME> <NUM_GAME> <HEIGHT> <WIDTH> <RANDOMNESS>
 *  - randomness is a float value in 0.0-1.0.
 *    larger value means agent choose more random moves
 *    0.0 means there is no random move,
 *    1.0 means every move is quite random
 *    Random moves may look like mistakes.
 *    In my experience, 0.05-0.15 is best for 11x11
 * Output Format:
 *  Each case begins with two integer '<WINNER> <NUM_MOVES>' separated by
 *  space. WINNER is 1 or 2. Following the first line, NUM_MOVES integers
 *  are given. Each moves are separated by newline. Moves are single integer,
 *  which is 'y * W + x'. e.g. In the board of width 11 and height 11,
 *  move 48 = 4 * 11 + 6 means the current player place a stone at
 *  (y, x) = (4, 6). Corrdinates are zero-based.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <omp.h>

int M = 1, W = 15, H = 15;
float rnd = 0.01;

FILE *f;

#define V_5 0x400
#define V_O4 0x100
#define V_O3 0x40
#define V_4 0x10
#define V_3 0x4
#define V_2 0x1

float randf() {
  return (float) rand() / (float) RAND_MAX;
}

float dist(int idx) {
  float y = (idx / W) - (H - 1) / 2;
  y /= (float) H;
  if(y < 0) y = -y;
  float x = (idx % W) - (W - 1) / 2;
  x /= (float) W;
  if(x < 0) x = -x;
  return x > y ? x : y;
}

typedef struct State {
  char *bd;
  int *his;
  int *val[2][5];
  int n;

  int result;

  char q[7];
  char qp;
  int idx[7];
  int n_c[4];
  int dir;
} State;

void printCell(State *S, int p, int dir, int idx) {
  int v = S->val[p][dir][idx];
  if(S->bd[idx] == p + 1) printf("  @");
  else if(S->bd[idx] == 2 - p) printf("  #");
  else if(v & V_5) printf("  5");
  else if(v & V_O4) printf(" +4");
  else if(v & V_O3) printf(" +3");
  else if(v & V_4) printf("  4");
  else if(v & V_3) printf("  3");
  else if(v & V_2) printf("  2");
  else printf("  .");
}

void printState(State *S) {
  char shape[] = {'.', 'O', 'X'};
  printf("=====================================================\n");
  printf("State %p, Turn %d, Result %d\n", S, S->n, S->result);
  printf("   |");
  for(int i = 0; i < W; i++) printf(" %2d", i);
  printf("\n");
  for(int i = 0; i < H; i++) {
    printf("%2d |", i);
    for(int j = 0; j < W; j++) {
      printf("  %c", shape[S->bd[i * W + j]]);
    }
    printf("\n");
  }
  /*
  for(int d = 1; d <= 4; d++) {
    const char *dir[5] = {"all", "hori", "vert", "rd", "ld"};
    printf("--------------- 0 %s\n", dir[d]);
    printf("   |");
    for(int i = 0; i < W; i++) printf(" %2d", i);
    printf("\n");
    for(int i = 0; i < H; i++) {
      printf("%2d |", i);
      for(int j = 0; j < W; j++) {
        printCell(S, 0, d, i * W + j);
      }
      printf("\n");
    }
    printf("---\n");
  }
  */
  char buf[24];
  fgets(buf, 24, stdin);
}

int getNext(State *S) {
#define ON 8
  float ov[ON];
  int oi[ON];
  for(int i = 0; i < ON; i++) {
    ov[i] = -1000.0f;
    oi[i] = -1;
  }
  int op = 0;
  int fl = 0;
  int off = rand() % H * W;
  for(int k = 0; k < H * W; k++) {
    int i = (off + k) % (H * W);
    if(S->bd[i] == 0) {
      float score = 0;
      if(S->n <= 2) score -= dist(i) * 10;
      int m = S->val[S->n % 2][0][i];
      int o = S->val[(S->n + 1) % 2][0][i];
      score += m + o * 0.7f;
      score += randf() * 0.5f;
      if(score > ov[op]) {
        oi[op] = i;
        ov[op] = score;
        if(score >= V_O3) fl = 1;
        op = (op + 1) % ON;
      }
    }
  }
  if(randf() < rnd / 2) {
    int x = rand() % ON;
    while(oi[x] < 0) x = (x + 1) % ON;
    return oi[x];
  } else {
    if(fl || randf() >= rnd) {
      int mi = -1;
      float mv = -100.0f;
      for(int i = 0; i < ON; i++) {
        if(oi[i] >= 0 && mv < ov[i]) {
          mi = oi[i];
          mv = ov[i];
        }
      }
      return mi;
    } else {
      int x = rand() % ON;
      while(oi[x] < 0) x = (x + 1) % ON;
      return oi[x];
    }
  }
}

void resetQ(State *S) {
  for(int i = 0; i < 7; i++) {
    S->q[i] = 3;
  }
  S->qp = 0;
  S->n_c[0] = 0, S->n_c[1] = 0, S->n_c[2] = 0, S->n_c[3] = 5;
}

void mark(State *S, int idx, char c, int val) {
  int i = S->idx[(S->qp + idx) % 7];
  if(0 == (S->val[c - 1][S->dir][i] & val)) {
    S->val[c - 1][S->dir][i] |= val;
    S->val[c - 1][0][i] += val;
  }
}

#define Q_AT(X) (S->q[((X) + S->qp + 7) % 7])
void check5(State *S, char c) {
  for(int i = 1; i <= 5; i++)
    mark(S, i, c, V_5);
}

void check4(State *S, char c) {
  for(int i = 1; i <= 5; i++)
    mark(S, i, c, V_4);
  if(Q_AT(0) == 0 && Q_AT(5) == 0)
    for(int i = 1; i <= 4; i++)
      mark(S, i, c, V_O4);
  if(Q_AT(1) == 0 && Q_AT(6) == 0)
    for(int i = 2; i <= 5; i++)
      mark(S, i, c, V_O4);
}

void check3(State *S, char c) {
  for(int i = 1; i <= 5; i++)
    mark(S, i, c, V_3);
  if(Q_AT(1) != 0 || Q_AT(5) != 0) return;
  if(Q_AT(2) == 0) {
    if(Q_AT(0) == 0) {
      mark(S, 1, c, V_O3);
      mark(S, 2, c, V_O3);
    } else if(Q_AT(6) == 0) {
      mark(S, 2, c, V_O3);
    }
  } else if(Q_AT(4) == 0) {
    if(Q_AT(6) == 0) {
      mark(S, 4, c, V_O3);
      mark(S, 5, c, V_O3);
    } else if(Q_AT(0) == 0) {
      mark(S, 4, c, V_O3);
    }
  } else {
    if(Q_AT(0) == 0) {
      mark(S, 1, c, V_O3);
      mark(S, 3, c, V_O3);
    }
    if(Q_AT(6) == 0) {
      mark(S, 3, c, V_O3);
      mark(S, 5, c, V_O3);
    }
  }
}

void check2(State *S, char c) {
  for(int i = 1; i <= 5; i++) {
    mark(S, i, c, V_2);
  }
}

void pushAndCheck(State *S, int idx, char v) {
  int p = S->qp;
  S->qp = (S->qp + 1) % 7;
  S->q[p] = v;
  S->idx[p] = idx;
  S->n_c[S->q[(p + 6) % 7]]++;
  S->n_c[S->q[(p + 1) % 7]]--;

  /*
  printf("[");
  for(int i = 0; i < 7; i++) {
    printf(" %d", S->q[(i + S->qp) % 7]);
  }
  printf("] (");
  for(int i = 0; i < 4; i++) {
    printf(" %d", S->n_c[i]);
  }
  printf(")\n");
  */

  if(S->n_c[3] == 0) {
    char c = 0;
    if(S->n_c[2] == 0) c = 1;
    else if(S->n_c[1] == 0) c = 2;
    if(c > 0) {
      switch(S->n_c[c]) {
      case 5: S->result = c;
      case 4: check5(S, c); break;
      case 3: check4(S, c); break;
      case 2: check3(S, c); break;
      case 1: check2(S, c); break;
      }
    }
  }
}

void removeVal(State *S, int idx) {
  S->val[0][S->dir][idx] = 0;
  S->val[1][S->dir][idx] = 0;
  for(int i = 1; i <= 4; i++) {
    S->val[0][0][idx] += S->val[0][i][idx];
    S->val[1][0][idx] += S->val[1][i][idx];
  }
}

int placeStone(State *S, int idx) {
  int y = idx / W;
  int x = idx % W;
  S->bd[idx] = 1 + (S->n % 2);
  S->n++;

  S->result = 0;
  // Hori
  S->dir = 1;
  for(int i = 0; i < W; i++)
    removeVal(S, y * W + i);
  resetQ(S);
  for(int i = 0; i < W; i++)
    pushAndCheck(S, y * W + i, S->bd[y * W + i]);
  pushAndCheck(S, -1, 3);
  // Vert
  S->dir = 2;
  for(int i = 0; i < H; i++)
    removeVal(S, i * W + x);
  resetQ(S);
  for(int i = 0; i < H; i++)
    pushAndCheck(S, i * W + x, S->bd[i * W + x]);
  pushAndCheck(S, -1, 3);
  // RD-Diag
  S->dir = 3;
  int rd = x < y ? x : y;
  int rdx = x - rd;
  int rdy = y - rd;
  for(int i = 0; rdx + i < W && rdy + i < H; i++)
    removeVal(S, (rdy + i) * W + (rdx + i));
  resetQ(S);
  for(int i = 0; rdx + i < W && rdy + i < H; i++)
    pushAndCheck(S, (rdy + i) * W + (rdx + i),
        S->bd[(rdy + i) * W + (rdx + i)]);
  pushAndCheck(S, -1, 3);
  // LD-Diag
  S->dir = 4;
  int ld = (W - x - 1) < y ? (W - x - 1) : y;
  int ldx = x + ld;
  int ldy = y - ld;
  for(int i = 0; ldx - i >= 0 && ldy + i < H; i++)
    removeVal(S, (ldy + i) * W + (ldx - i));
  resetQ(S);
  for(int i = 0; ldx - i >= 0 && ldy + i < H; i++)
    pushAndCheck(S, (ldy + i) * W + (ldx - i),
        S->bd[(ldy + i) * W + (ldx - i)]);
  pushAndCheck(S, -1, 3);
  return S->result;
}

void runGame() {
  printf("Thread %d Start\n", omp_get_thread_num());

  State S;
  S.bd = (char*) malloc(sizeof(char) * W * H);
  S.his = (int*) malloc(sizeof(int) * W * H);
  for(int i = 0; i < 2; i++)
    for(int j = 0; j < 5; j++) {
      S.val[i][j] = (int*) malloc(sizeof(int) * W * H);
    }

  int finished = 0;

  while(1) {
    memset(S.bd, 0x00, sizeof(char) * W * H);
    for(int i = 0; i < 2; i++) {
      for(int j = 0; j < 5; j++) {
        memset(S.val[i][j], 0x00, sizeof(int) * W * H);
      }
    }
    S.n = 0;

    //printState(&S);
    while(S.n < W * H) {
      int idx = getNext(&S);
      S.his[S.n] = idx;
      finished = placeStone(&S, idx);
    //printState(&S);

      if(finished) {
#pragma omp critical(WRITE_FILE)
        {
          fprintf(f, "%d %d\n", S.result, S.n);
          for(int i = 0; i < S.n; i++) {
            fprintf(f, "%d\n", S.his[i]);
          }
        }
        goto L_DONE;
      } 
    }
  }
L_DONE:
  free(S.bd);
  free(S.his);
  for(int i = 0; i < 2; i++)
    for(int j = 0; j < 5; j++)
      free(S.val[i][j]);

  printf("Thread %d Finished\n", omp_get_thread_num());
}

int main(int argc, char **argv) {
  srand(time(NULL));
  printf("ARGC = %d\n", argc);
  if(argc < 6) {
    fprintf(stderr,
        "Usage: %s <OUT_NAME> <MAX> <HEIGHT> <WIDTH> <RND>\n",
        argv[0]);
    return 1;
  }
  M = atoi(argv[2]);
  H = atoi(argv[3]);
  W = atoi(argv[4]);
  rnd = atof(argv[5]);
  printf("OUT=%s MAX=%d H=%d W=%d RND=%f\n", argv[1], M, H, W, rnd);

  f = fopen(argv[1], "w");
  if(f == NULL) {
    fprintf(stderr, "Cannot open file %s\n", argv[1]);
    return NULL;
  }

#pragma omp parallel for num_threads(8)
  for(int i = 0; i < M; i++) {
    runGame();
  }

  fclose(f);
  return 0;
}
