int main() {
    int sum = 0;
  
    for (int i = 0; i < 5; i++) {
      int z = 8 * i;
      int w = 64 / 4;
      int temp = 2 * w;
      sum += z + temp;
    }
  
    int unused = 0;
    return sum;
  }
  