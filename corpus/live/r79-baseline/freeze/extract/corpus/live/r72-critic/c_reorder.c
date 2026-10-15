/* r72-critic: is the reorder topology specific to CPython, or a
 * libc-stdio property?  Same parent role as reorder_demo.py, in C.
 *
 *   ./c_reorder            -> default stdio on a pipe: fully buffered
 *   ./c_reorder flush-head -> explicit fflush after HEAD (unbuffered-like)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    int flush_head = (argc > 1 && strcmp(argv[1], "flush-head") == 0);
    fputs("HEAD\n", stdout);
    if (flush_head) {
        fflush(stdout);
    }
    system("printf 'CHILD\\n'");   /* write-through descendant, inherited fd1 */
    fputs("TAIL\n", stdout);
    return 0;                      /* exit flushes whatever remains */
}
