#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void win() {
    printf("🏁 FLAG: CTF{format_string_and_overflow_mastery}\n");
    fflush(stdout);
    exit(0);
}

void vuln() {
    char buffer[64];
    char input[256];

    printf("Enter input: ");
    fflush(stdout);
    fgets(input, sizeof(input), stdin);

    // Vulnerable: format string bug
    printf(input);

    // Copy again for overflow
    printf("\nOverflow buffer: ");
    fflush(stdout);
    gets(buffer); // buffer overflow here

    printf("You entered: %s\n", buffer);
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0); // disable buffering
    vuln();
    return 0;
}
