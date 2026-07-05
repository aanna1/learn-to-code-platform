/* Reference solution. Returns 1 + 2 + ... + n (and 0 for n <= 0). */
#include <stdio.h>

int sum_to(int n) {
    int total = 0;
    for (int i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}

/* A main() for the Run button. The grader neutralizes it via -Dmain=__student_main__. */
int main(void) {
    printf("sum_to(10) = %d\n", sum_to(10));
    return 0;
}
