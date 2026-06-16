# FPGA Implementation of an LFSR-Based Shrinking Generator

## Overview
This project presents the design, implementation, and verification of a nonlinear keystream generator based on the Shrinking Generator architecture. The design combines a 31-bit selector LFSR and a 32-bit data LFSR to reduce the linearity of conventional LFSR-based generators.

The system was implemented in VHDL, verified through simulation and synthesis, and validated on FPGA hardware.

## Architecture
- 31-bit LFSR (Selector)
- 32-bit LFSR (Data)
- Shrinking Generator Logic
- FPGA Implementation

## Features
- Maximum-period LFSR design
- Nonlinear keystream generation using the Shrinking Generator architecture
- Modular VHDL implementation
- Functional simulation and synthesis verification
- FPGA hardware validation

## Tools
- VHDL
- Xilinx Vivado

## Author
Eren Dikmen  
Ankara University – Electrical and Electronics Engineering
