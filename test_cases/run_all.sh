#!/bin/bash

# Output file
OUTFILE="results.txt"
echo "==== Performance Evaluation Report ====" > "$OUTFILE"
echo "" >> "$OUTFILE"

# Compile both programs with profiling and debug symbols
gcc -pg -g -o original main_input6.c
gcc -pg -g -o optimized output6.c

# ----------- TIME -----------
echo "===> Timing: original" >> "$OUTFILE"
{ /usr/bin/time -f "\nreal %e\nuser %U\nsys %S" timeout 5s ./original > /dev/null; } 2>> "$OUTFILE"

echo "" >> "$OUTFILE"

echo "===> Timing: optimized" >> "$OUTFILE"
{ /usr/bin/time -f "\nreal %e\nuser %U\nsys %S" timeout 5s ./optimized > /dev/null; } 2>> "$OUTFILE"

echo "" >> "$OUTFILE"

# ----------- VALGRIND -----------
echo "===> Valgrind: original" >> "$OUTFILE"
timeout 5s valgrind --leak-check=full ./original >> "$OUTFILE" 2>&1

echo "" >> "$OUTFILE"

echo "===> Valgrind: optimized" >> "$OUTFILE"
timeout 5s valgrind --leak-check=full ./optimized >> "$OUTFILE" 2>&1

echo "" >> "$OUTFILE"

# ----------- GPROF -----------
echo "===> Gprof: original" >> "$OUTFILE"
timeout 5s ./original
gprof original gmon.out >> "$OUTFILE" 2>&1
mv gmon.out gmon_original.out 2>/dev/null

echo "" >> "$OUTFILE"

echo "===> Gprof: optimized" >> "$OUTFILE"
timeout 5s ./optimized
gprof optimized gmon.out >> "$OUTFILE" 2>&1
mv gmon.out gmon_optimized.out 2>/dev/null

echo "" >> "$OUTFILE"

echo "✅ Done. Results saved to results.txt"
