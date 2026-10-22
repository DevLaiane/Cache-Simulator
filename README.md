# Cache-Simulator

This project is a memory cache simulator developed in Python. The program reads a binary file containing a sequence of memory addresses (4-byte big-endian format) and simulates the behavior of a configurable cache.

## Features

- **Flexible configuration:** Allows setting the number of sets (`nsets`), block size (`bsize`), and associativity (`assoc`).
- **Replacement policies:** Supports direct mapping and set-associative mapping, using **Random (R)**, **FIFO (F)**, and **LRU (L)** policies.
- **Performance statistics:** Calculates and displays *Hit* rates, *Miss* rates, *Compulsory Misses*, *Capacity Misses*, and *Conflict Misses*.
- **Output formats:** Detailed output (flag 0) or summarized output (flag 1).

## How to use

Run the script passing the parameters via command line:

```bash
python3 simulador.py <nsets> <bsize> <assoc> <replacement> <output_flag> input_file
