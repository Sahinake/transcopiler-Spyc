#include <stdio.h>
#include <string.h>

int soma(int a, int b) {
    return (a + b);
}

float media(float x, float y, float z) {
    return (((x + y) + z) / 3);
}

int main() {
    // esse é um comentário de topo
    int y = soma(2, 3);
    int z = media(1.0, 2.5, 4.5);
    char name[256];
    printf("Enter your name: ");
    scanf("%255s", name);
    char age[256];
    printf("Enter your age: ");
    scanf("%255s", age);
    printf("%s %s\n", "Hello,", name);
    printf("%s %s %s\n", "You are", age, "years old");
    // fim do arquivo
    return 0;
}