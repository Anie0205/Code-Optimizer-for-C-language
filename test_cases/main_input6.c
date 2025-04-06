int compute(int x) {
    int a;
    int b;
    int unused;
    int i;
    int j;
    int k;

    a = 10 * 5;
    b = a + x;
    unused = x * 999;

    i = 0;
    while (i < 1000) {
        j = 0;
        while (j < 500) {
            k = (j * 2) + (i * 3);
            b = b + (k % 10);
            j = j + 1;
        }
        i = i + 1;
    }

    return b;
}

int main() {
    int result;
    int i;

    result = 0;
    i = 0;
    while (i < 50) {
        result = result + compute(i);
        i = i + 1;
    }

    return result;
}
