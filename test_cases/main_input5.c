int main() {
    int a = 2 * 4;      
    int b = a + 2 * 4;  
    int c = b * 1;      
  
    if (1) {
      int x = 3 * 2;
      a = x + 0;
    }
  
    for (int i = 0; i < 2; i++) {
      int t = 32 * i;  
      int z = a + b;
      int y = 3 * 2;   
      c += t + z + y;
    }
  
    if (0) {
      int junk = 999;
    }
  
    return c;
  }
  