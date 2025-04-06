int main() {
    int a = 4 * 2;
    int b = 16 / 2;
    int c = a + b;
  
    if (0) {
      c = 999;
    }
  
    int result = 0;
    for (int i = 0; i < 4; i++) {
      int x = 3 * 4;
      result += x * i + x * i;
    }
  
    return result + c;
  }  