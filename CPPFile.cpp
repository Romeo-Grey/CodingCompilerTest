#include <iostream>
int main() {
    int x = 5;
    int y = 10;
L1:
    // TODO: < x 10 T1
    if (NOT T1) goto L2;
    std::cout << x << std::endl;
    // TODO: + x 1 T2
    int x = T2;
    // TODO: > y 5 T3
    if (T3) goto L3;
    goto L4;
L3:
    std::cout << ""y is greater than 5"" << std::endl;
    goto L5;
L4:
    std::cout << ""y is not greater than 5"" << std::endl;
    // TODO: + x y T4
    int z = T4;
    std::cout << z << std::endl;
L5:
    goto L1;
L2:
    return 0;
}