#include <stdio.h>
#include <string.h>

void soma(int a, int b) {
    return (a + b);
}
void media(float x, float y, float z) {
    return (((x + y) + z) / 3);
}
int main() {
    // esse é um comentário de topo
    int y = soma(2, 3);
    int z = media(1.0, 2.5, 4.5);
    // fim do arquivo
    return 0;
}