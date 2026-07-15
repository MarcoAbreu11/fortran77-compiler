# Fortran 77 Compiler for VM

Practical assignment for **Language Processing**.

The objective of the project was to build a simple compiler for a subset of Fortran 77, directly generating code for the virtual machine used in the course.

The complete explanation of the decisions made, the grammar, the difficulties, and the implementation is in the technical report. This README serves only as a quick guide to understanding the project structure and running the tests.

## Project Structure

```text
CompiladorFortran/
  AST.py              # abstract syntax tree nodes
  AnalexFortran.py    # lexical analyzer
  AnasinFortran.py    # syntactic analyzer and entry point used in tests
  AnaSemantica.py     # semantic validations
  TabelaSimbolos.py   # symbol table construction
  codegen.py          # code generation for the VM

Testes/
  ola.txt
  fatorial.txt
  primo.txt
  soma.txt
  conversao.txt
```

## Main Features

The compiler supports the necessary subset for the assignment examples:

- `PROGRAM ... END`
- `INTEGER`, `REAL`, and `LOGICAL` variables
- one-dimensional arrays
- assignments
- arithmetic, relational, and logical expressions
- `IF`, `ELSE`, `ENDIF`
- `DO` loops
- `GOTO` and labels
- `READ *` and `PRINT *`
- `MOD(...)`
- minimal support for `INTEGER FUNCTION`, used in the base conversion example

Optimizations or extra features outside what was necessary for the assignment were not implemented.

## Requirements

Python 3 is required.

It is also necessary to install PLY:

```bash
pip install ply
```

## How to Run and Test

The main analyzer is located in `AnasinFortran.py`. The interface was updated to facilitate use via `stdin` and batch execution.

**1. Compile a specific file (via stdin):**
The compiler reads the source code from standard input (`stdin`) and prints the generated object code to the terminal.
```bash
cd CompiladorFortran
python AnasinFortran.py < ../Testes/fatorial.txt > fatorial.vm
```

**2. Run the automatic test suite:**
The project includes a test mode that reads all files in the `Testes/` folder, compiles them, and saves the resulting files.
```bash
cd CompiladorFortran
python AnasinFortran.py --test
# or
python AnasinFortran.py -t
```

After generating the VM code, it can be executed in the virtual machine of the course.

## Observations

The project was done in a simple and direct way: the frontend handles lexical, syntactic, and semantic analysis, while the backend traverses the validated AST and generates the VM code.

The main idea was to properly fulfill the subset requested in the assignment, without complicating the solution with features that were not necessary for the provided tests.
