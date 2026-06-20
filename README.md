# FPGA Implementation of an LFSR-Based Shrinking Generator

## Overview

This project presents the design, implementation, and verification of a nonlinear keystream generator based on the Shrinking Generator architecture. The design combines a 31-bit selector LFSR and a 32-bit data LFSR to reduce the linearity of conventional LFSR-based pseudo-random generators.

The system was implemented in VHDL, verified through simulation and synthesis, and validated on FPGA hardware.

## Architecture

The Shrinking Generator consists of two independent Linear Feedback Shift Registers:

* 31-bit LFSR used as the selector register
* 32-bit LFSR used as the data register
* Shrinking logic that accepts or discards data bits according to the selector output

At each clock cycle, both LFSRs generate one output bit. If the selector bit is `1`, the corresponding data bit is accepted as part of the output keystream. If the selector bit is `0`, the data bit is discarded.

## LFSR Configuration

For an N-bit LFSR with a primitive feedback polynomial, the maximum theoretical period is:

```text
2^N - 1
```

In this project:

```text
31-bit selector LFSR feedback = bit0 ⊕ bit3
32-bit data LFSR feedback     = bit0 ⊕ bit1 ⊕ bit2 ⊕ bit22
```

Both LFSRs are initialized with non-zero seed values to avoid the all-zero lock-up state.

## Output Signals

The output bit of each LFSR is taken from `r(0)` because the implemented LFSRs are right-shift registers.

In the Shrinking Generator:

```text
valid_o = selector bit
bit_o   = accepted data bit when valid_o = 1
```

When `valid_o` is `0`, the current data bit is discarded and `bit_o` should be ignored.

## Project Files

The main VHDL files are:

```text
lfsr31.vhd
lfsr32.vhd
shrinking_generator.vhd
tb_shrinking.vhd
```

These files contain the hardware description and testbench used for simulation and verification.

## Educational Simulator

An interactive educational simulator is included in this repository. The simulator visualizes the operation of the Shrinking Generator step by step.

The simulator shows:

* 31-bit selector LFSR state
* 32-bit data LFSR state
* XOR feedback calculations
* Feedback insertion into the MSB
* Selector-based accept/discard decision
* Output pool formation
* Step-by-step clock cycle behavior

The simulator is useful for understanding the difference between:

```text
feedback bit  -> used to calculate the next LFSR state
output bit    -> used in the Shrinking Generator decision
```

## Running the Simulator

Simulator files can be found in the simulator-related folder or package included in this repository.

### Windows

To run directly:

```text
run_with_python.bat
```

To build an executable file:

```text
build_windows_exe.bat
```

The generated executable will be created under:

```text
dist/ShrinkingGeneratorSimulator.exe
```

### macOS

To run directly:

```text
run_macos.command
```

To build a macOS application:

```text
build_macos_app.command
```

The generated application will be created under:

```text
dist/ShrinkingGeneratorSimulator.app
```

If macOS blocks the command file due to permissions, run:

```bash
chmod +x run_macos.command
chmod +x build_macos_app.command
```

## Tools Used

* VHDL
* Xilinx Vivado
* FPGA hardware validation
* Python
* Tkinter

## References

[1] A. J. Menezes, P. C. van Oorschot, and S. A. Vanstone, *Handbook of Applied Cryptography*, CRC Press, 1996.

[2] D. Coppersmith et al., “The Shrinking Generator,” *CRYPTO ’93*, LNCS 773, pp. 22–39, Springer, 1994.

## Author

Eren Dikmen
Ankara University
Electrical and Electronics Engineering
