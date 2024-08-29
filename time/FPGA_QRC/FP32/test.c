#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    srand(time(NULL));  // Seed the random number generator

    // Test rand() output
    for (int i = 0; i < 10; i++) {
        printf("rand() output: %d\n", rand());
    }

    return 0;
}