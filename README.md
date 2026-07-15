# Fortran 77 Compiler for VM

A compiler for a subset of Fortran 77, developed in Python using the PLY (Python Lex-Yacc) library. This project was built for the **Language Processing and Compilers** course at the **University of Minho**.

## Overview

This project implements a complete compilation pipeline, translating a specific subset of Fortran 77 into instructions for a custom stack-based [Virtual Machine](https://ewvm.epl.di.uminho.pt/). The pipeline operates through the following stages:

1. **Lexical Analysis:** Tokenization of the source code.
2. **Syntactic Analysis:** Grammar parsing and structural validation.
3. **Abstract Syntax Tree (AST):** Construction of a hierarchical representation of the code.
4. **Semantic Analysis:** Scope handling, type and declaration checking, and ambiguous reference resolution.
5. **Code Generation:** Translation of the validated AST into virtual machine instructions.

## Supported Features

The compiler supports the necessary language constructs to execute a variety of algorithms, including:

* **Data Types:** `INTEGER`, `REAL`, and `LOGICAL` variables.
* **Data Structures:** Scalar variables and one-dimensional arrays.
* **Expressions:** Arithmetic, logical, and relational operations with proper precedence.
* **Control Flow:** `IF`, `IF...ELSE`, labelled `DO` loops, and `GOTO` statements.
* **Input/Output:** `READ *` and `PRINT *` (supporting strings, integers, reals, and logicals).
* **Functions:** Minimal support for `INTEGER FUNCTION`, including parameter passing, function calls within expressions, and `RETURN`.
* **Built-in Functions:** Support for `MOD(...)`.

## Technologies Used

* **Python 3**
* **PLY (Python Lex-Yacc):** Utilized for the `lex` and `yacc` modules to build the frontend.

## Project Structure

```text
.
├── src/
│   ├── AnalexFortran.py    # Lexical analyzer
│   ├── AnaSemantica.py     # Semantic validations and scope rules
│   ├── AnasinFortran.py    # Syntactic analyzer & main entry point
│   ├── AST.py              # Abstract Syntax Tree nodes representation
│   ├── codegen.py          # Code generation for the VM
│   └── TabelaSimbolos.py   # Symbol table construction
├── tests/
│   ├── conversao.txt       # Decimal conversion to bases 2-9
│   ├── fatorial.txt        # Factorial calculation
│   ├── ola.txt             # Hello world
│   ├── primo.txt           # Prime number verification
│   └── soma.txt            # Array summation
├── report.md
└── README.md
```

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
python AnasinFortran.py < ../Testes/fatorial.txt 
```

**2. Run the automatic test suite:**
The project includes a test mode that reads all files in the `Testes/` folder, compiles them, and saves the resulting files.
```bash
python AnasinFortran.py --test
# or
python AnasinFortran.py -t
```

After generating the VM code, it can be executed in the [Virtual Machine](https://ewvm.epl.di.uminho.pt/) of the course.

## Academic Context

* **Course:** Language Processing and Compilers
* **Degree:** Computer Science
* **Institution:** University of Minho
* **Academic Year:** 2025/2026
* **Project Grade:** 17/20
* **Type:** Group Project
