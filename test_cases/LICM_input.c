int main() {
  int x = 10;
  int y = 5;
  int sum = 0;
  
  for (int i = 0; i < 4; i++) {
      int z = x + y;
      sum += z * i;
  }
  
  return sum;
}
