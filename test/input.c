int main()
{
    int a = 1;
    int x = 123;
    float y = .5;
    char z = 'C';
    bool flag = 1;
    int array[5] = {1, 2, 3, 4, 5};
    if ((a >= 5 || a < 3) && (a == 7))
    {
        a = a + 1;
    }
    if ((a <= 10 && a != 8) || (a > 2))
    {
        a = a - 1;
        a = a % 2;
    }
    a = x + y;
    a = array[2] * array[3] / array[1];

    flag = !flag;

    // Comentário

    return 0;
}