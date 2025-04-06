int main() {
    int total = 0;
    int factor = 2 * 2;
  
    for (int i = 0; i < 3; i++) {
      int temp = 4 * 5;
      for (int j = 0; j < 2; j++) {
        int common = temp + factor;
        total += common + temp + factor;
      }
  
      if (0) {
        total -= 100;
      }
    }
  
    return total;
  }
  