#include <stdio.h>
#include <string.h>

int soma(int a, int b) {
    return (a + b);
}

float multiplica(float x, float y) {
    return (x * y);
}

int main() {
    // ==== Funções com tipos e retorno ====
    // ==== Uso de variáveis com tipos diferentes ====
    int numero = 7;
    float preco = 19.99;
    char* saudacao = "Olá, Mundo!";
    // ==== Chamada de funções ====
    // parâmetros tipo int
    int resultado = soma(3, numero);
    // parâmetros tipo float
    float total = multiplica(2.5, 4.0);
    // ==== Entrada do usuário ====
    char nome[256];
    printf("Digite seu nome: ");
    scanf("%255s", nome);
    char idade[256];
    printf("Digite sua idade: ");
    scanf("%255s", idade);
    // ==== Saída para o usuário ====
    printf("%s %s\n", "Nome:", nome);
    printf("%s %s\n", "Idade:", idade);
    printf("%s %s\n", "Mensagem:", saudacao);
    printf("%s %d\n", "Resultado da soma:", resultado);
    printf("%s %f\n", "Total da multiplicação:", total);
    // ==== Bloco condicional ====
    if ((total > 30.0)) {
        printf("%s\n", "Tá muito caro!");
    } else {
        printf("%s\n", "Tá baratim!");
    }
    // ==== Comentário de fim de arquivo ====
    // Tudo funcionando como esperado!
    return 0;
}