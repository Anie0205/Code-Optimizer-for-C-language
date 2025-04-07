int main()
{
  int x = 10;
  int y = 5;
  int sum = 0;
  int _t0 = x + y;
  for (int i = 0; i < 4; i++)
  {
    int z = _t0;
    sum += z * i;
  }

  return sum;
}

