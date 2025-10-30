#!/usr/bin/env python3

import sys
import extract

# We need 17 arguments *plus* the script name (sys.argv[0]).
# Therefore, the total length of sys.argv must be at least 18.
if len(sys.argv) < 18:
    # Instead of 'pass', it's better to print an error and exit
    # if the arguments are incorrect.
    print(
        f"Error: Incorrect number of arguments. Expected 17, got {
            len(
                sys.argv) -
            1}",
        file=sys.stderr)
    print(f"Usage: {sys.argv[0]} <arg1> <arg2> ... <arg17>", file=sys.stderr)
    sys.exit(1)
else:
    # Pass the 17 arguments (from index 1 to 17)
    extract.NEOBootMainEx(
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
        sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8],
        sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12],
        sys.argv[13], sys.argv[14], sys.argv[15], sys.argv[16],
        sys.argv[17]
    )

    # Note: A cleaner, more "Pythonic" way to write the 'else' block
    # (assuming NEOBootMainEx accepts 17 distinct arguments)
    # would be to use argument unpacking:
    #
    # args = sys.argv[1:18]
    # extract.NEOBootMainEx(*args)
