# Report — Fortran 77 Compiler for Virtual Machine

**Course:** Language Processing

**Assignment:** Compiler of a subset of Fortran 77 for the provided virtual machine

**Authors:** Cláudio Rafael Oliveira Ferreira (a108577) and Marco António Ferreira Abreu (a108578)  

## 1. Introduction

The objective of this assignment was to develop a compiler for a simple subset of Fortran 77, generating as output code for the virtual machine provided in the course. Our priority was to correctly fulfill the essential requirements of the assignment, without adding unnecessary features that would increase the complexity of the project.

Since the group consisted of only two members, we opted for a direct and easy-to-understand implementation. The compiler was divided into two main parts: the compiler frontend, responsible for lexical, syntactic, and semantic analysis, and code generation, responsible for traversing the already validated abstract syntax tree and producing virtual machine instructions.

The delivered version supports the five examples provided in the assignment: simple printing, factorial calculation, primality testing, array summation, and conversion of a decimal number to various bases using an `INTEGER FUNCTION`. This last feature was included minimally, only to the extent necessary for the corresponding example, and not as full support for Fortran subprograms.

## 2. Solution Organization

The implementation was done in Python, using the PLY library to build the lexical and syntactic analyzer. The project is organized into several files, each with a well-defined responsibility:

| File | Responsibility |
|---|---|
| `AnalexFortran.py` | Defines tokens, reserved words, literals, operators, and lexical rules. |
| `AnasinFortran.py` | Defines the grammar and builds the initial AST. |
| `AST.py` | Contains the classes used to represent the abstract syntax tree nodes. |
| `TabelaSimbolos.py` | Builds the symbol table, separating the main program scope from the functions. |
| `AnaSemantica.py` | Validates types, scopes, labels, arrays, functions, and transforms ambiguous references into final nodes. |
| `codegen.py` | Traverses the validated AST and generates virtual machine code. |
| `Testes/` | Contains the Fortran programs used to test the main examples. |

This separation was important because it avoided mixing parsing, semantic validation, and code generation in the same place. Code generation assumes that the AST is already clean and validated, which greatly simplifies the backend.

## 3. Supported Language Subset

The compiler supports a subset of Fortran 77 sufficient for the requested examples. The implemented constructs were:

- `PROGRAM ... END`;
- `INTEGER`, `REAL`, and `LOGICAL` declarations;
- scalar variables;
- one-dimensional arrays;
- assignments;
- arithmetic, relational, and logical expressions;
- integer, real, logical, and string literals in `PRINT`;
- `IF ... THEN ... ENDIF`;
- `IF ... THEN ... ELSE ... ENDIF`;
- `DO` loops with final label and `CONTINUE`;
- `GOTO` and numeric labels;
- `READ *`;
- `PRINT *`;
- `MOD` function;
- minimal support for `INTEGER FUNCTION`;
- function calls within expressions;
- `RETURN` inside functions.

More advanced features such as `SUBROUTINE`, `CALL`, recursion, multidimensional arrays, `COMMON`, `DATA`, `FORMAT`, `WRITE`, `CHARACTER` as a variable type, array passing as arguments, and code optimizations were left out of scope.

This decision was intentional. We preferred to implement fewer features, but ensure that the implemented features worked predictably and were aligned with the assignment description.

## 4. Grammar Used

The grammar was written in the `AnasinFortran.py` file using PLY/Yacc. Below is a summarized version of the actual grammar used, with the main groups of rules.

```bnf
inicio              : programa lista_funcoes
lista_funcoes       : lista_funcoes funcao
                    | vazio

programa            : PROGRAM ID lista_instrucao END
funcao              : tipo FUNCTION ID LPAREN lista_parametros RPAREN lista_instrucao END

lista_parametros    : lista_parametros_ext
                    | vazio
lista_parametros_ext: lista_parametros_ext COMMA ID
                    | ID

lista_instrucao     : lista_instrucao instrucao
                    | instrucao

instrucao           : instrucao_sem_label
                    | label instrucao_sem_label

instrucao_sem_label : declaracao
                    | atribuicao
                    | comando_if
                    | comando_do
                    | comando_goto
                    | comando_print
                    | comando_read
                    | comando_continue
                    | comando_return

label               : INTEGER_LIT

declaracao          : tipo lista_variaveis
tipo                : INTEGER
                    | REAL
                    | LOGICAL

lista_variaveis     : lista_variaveis COMMA variavel_decl
                    | variavel_decl
variavel_decl       : ID
                    | ID LPAREN INTEGER_LIT RPAREN

atribuicao          : referencia ASSIGN expressao
referencia          : ID
                    | ID LPAREN lista_argumentos RPAREN
```

The main command rules were:

```bnf
comando_if          : IF expressao THEN lista_instrucao ENDIF
                    | IF expressao THEN lista_instrucao ELSE lista_instrucao ENDIF

comando_do          : DO label ID ASSIGN expressao COMMA expressao opt_step lista_instrucao label CONTINUE
opt_step            : COMMA expressao
                    | vazio

comando_goto        : GOTO label
comando_continue    : CONTINUE
comando_return      : RETURN

comando_print       : PRINT TIMES COMMA lista_prints
lista_prints        : lista_prints COMMA elemento_print
                    | elemento_print
elemento_print      : STRING
                    | expressao

comando_read        : READ TIMES COMMA lista_reads
lista_reads         : lista_reads COMMA referencia
                    | referencia
```

The expressions were organized by precedence levels, starting with logical operators, then comparisons, then arithmetic operators:

```bnf
expressao           : expressao OR termo_logico
                    | termo_logico

termo_logico        : termo_logico AND fator_logico
                    | fator_logico

fator_logico        : NOT fator_logico
                    | comparacao

comparacao          : expressao_aritmetica EQ expressao_aritmetica
                    | expressao_aritmetica NE expressao_aritmetica
                    | expressao_aritmetica LT expressao_aritmetica
                    | expressao_aritmetica LE expressao_aritmetica
                    | expressao_aritmetica GT expressao_aritmetica
                    | expressao_aritmetica GE expressao_aritmetica
                    | expressao_aritmetica

expressao_aritmetica: expressao_aritmetica PLUS termo
                    | expressao_aritmetica MINUS termo
                    | termo

termo               : termo TIMES fator
                    | termo DIVIDE fator
                    | fator

fator               : MINUS fator
                    | primario

primario            : INTEGER_LIT
                    | REAL_LIT
                    | TRUE
                    | FALSE
                    | referencia
                    | LPAREN expressao RPAREN
                    | MOD LPAREN expressao COMMA expressao RPAREN

lista_argumentos    : lista_argumentos_ext
                    | vazio
lista_argumentos_ext: lista_argumentos_ext COMMA expressao
                    | expressao
```

An important decision was to let the `referencia` rule accept both `ID` and `ID(...)`. Syntactically, `ID(...)` can be an array access or a function call. This ambiguity was not resolved in the grammar, but in the semantic analysis, because only the symbol table knows if the name represents an array or a function.

## 5. Internal Representation: AST

After the syntactic analysis, the program is represented through an abstract syntax tree. The nodes are defined in `AST.py`.

The root node is `CompilationUnit`, which contains the main program and the list of functions:

```python
CompilationUnit(program, functions)
```

The main program is represented by:

```python
Program(name, body)
```

Functions are represented by:

```python
FunctionDef(name, return_type, params, body)
```

Specific nodes were created for commands, expressions, and literals. For example:

- `Assign` for assignments;
- `If` for conditionals;
- `DoLoop` for `DO` loops;
- `Goto` and `Label` for jumps;
- `Print` and `Read` for input/output;
- `Var`, `ArrayAccess`, and `FunctionCall` for resolved references;
- `BinOp`, `UnaryOp`, and `Mod` for expressions;
- `IntLiteral`, `RealLiteral`, `LogicalLiteral`, and `StringLiteral` for literals.

During parsing, a reference is initially represented by the auxiliary node `Referencia`. After the semantic analysis, this node is replaced by one of the final nodes:

```python
Var(...)
ArrayAccess(...)
FunctionCall(...)
```

This transformation was one of the most important decisions of the work, because it meant the code generator did not have to guess if `A(I)` was an array or a function. When the backend receives the AST, this decision has already been made.

## 6. Symbol Table and Semantic Analysis

The symbol table is built before the complete semantic validation. It stores the necessary information about variables, arrays, parameters, functions, and labels.

The structure separates two types of scope:

1. main program scope;
2. function scopes.

Simplified, the table looks like this:

```python
{
    "program": {
        "name": "...",
        "symbols": {...},
        "labels": {...}
    },
    "functions": {
        "FUNCTION_NAME": {
            "return_type": "integer",
            "params": [...],
            "locals": {...},
            "labels": {...}
        }
    }
}
```

Each symbol has at least a type and a category (`kind`). The categories used were:

- `scalar`, for scalar variables;
- `array`, for one-dimensional arrays;
- `param`, for function parameters;
- `function_ref`, for function names visible in the main program;
- `return_var`, for the return variable of a function.

The semantic analysis validates the main aspects before code generation:

- use of declared variables;
- repetition of names in the same scope;
- distinction between scalar, array, and function;
- correct number of arguments in function calls;
- function argument types;
- integer array indices;
- `IF` with logical condition;
- `DO` with integer control variable;
- existence of labels used in `GOTO`;
- rejection of `RETURN` outside a function;
- existence of `RETURN` inside functions;
- rejection of assignment to parameters;
- rejection of direct recursion.

In addition, the semantic analysis assigns the `result_type` to expressions. Thus, for example, a sum between integers is marked as `integer`, a comparison is marked as `logical`, and an operation between reals is marked as `real`. This allows the backend to directly choose between integer and real virtual machine instructions.

## 7. Code Generation for the Virtual Machine

Code generation is concentrated in the `codegen.py` file. The main class is `CodeGen`, which keeps the list of generated instructions, active scopes, and a counter for internal labels.

The generation follows a simple rule: each expression leaves its result on the top of the stack. From there, virtual machine instructions consume the stack values and produce the expected result.

### 7.1 General Program Structure

The `gen_CompilationUnit` method is the backend's entry point. The generated order is:

```text
pushn <number of global cells>
start
<main program code>
stop
<functions code>
```

Functions are emitted after `stop`, so they are not executed directly. They are only executed when there is a call with `pusha <label>` followed by `call`.

### 7.2 Memory Management

To simplify variable management, the `Scope` class was created. Each scope stores variable offsets and the next free index.

In the main program, variables live in the VM's global area. Therefore, reading and writing are done with:

```text
pushg <offset>
storeg <offset>
```

In functions, the VM uses `fp`. Parameters are at negative offsets and local variables are at positive offsets. For example, in a function called as `CONVRT(NUM, BASE)`, arguments are pushed from left to right. Inside the function:

```text
N    -> fp[-2]
B    -> fp[-1]
```

Local variables and the return variable are reserved with `pushn k` at the beginning of the function and accessed with `pushl` and `storel`.

### 7.3 Literals and Variables

Literals are translated directly:

```text
integer  -> pushi value
real     -> pushf value
logical  -> pushi 0 or pushi 1
string   -> pushs "text"
```

The `LOGICAL` type was represented as an integer, using `0` for false and `1` for true. This choice fits well with the VM's comparison and conditional jump instructions.

### 7.4 Expressions

Binary expressions are always generated in the same order:

```text
<left code>
<right code>
<operator>
```

This is important because the VM is a stack machine. In operations like subtraction, division, and comparison, the operand order alters the result.

For integer operations, instructions like the following were used:

```text
add, sub, mul, div, mod
```

For reals, we used:

```text
fadd, fsub, fmul, fdiv
```

For comparisons, instructions like `inf`, `infeq`, `sup`, `supeq` were used for integers, and their real versions `finf`, `finfeq`, `fsup`, `fsupeq` for reals. The difference between `==` and `!=` was implemented with `equal` and, in the case of not equal, `equal` followed by `not`.

### 7.5 Assignments

An assignment to a scalar variable follows the pattern:

```text
<expression code>
storeg/storel <offset>
```

In the case of arrays, the element's address is calculated first, then the value is generated, and finally `store 0` is emitted:

```text
<element address>
<value>
store 0
```

### 7.6 Arrays

Arrays are one-dimensional and occupy a contiguous block of memory. Since Fortran indices start at 1, but in the VM memory we use offsets from 0, an adjustment was necessary:

```text
real_index = fortran_index - 1
```

An element's address is calculated with:

```text
array_base + (index - 1)
```

In the VM, this is done using `pushgp` or `pushfp`, `padd`, `load 0`, and `store 0`. To read `NUMS(I)`, for instance, the generated pattern is:

```text
pushgp
pushi <base_offset>
padd
<code of I>
pushi 1
sub
padd
load 0
```

This point was especially important in the array summation example.

### 7.7 PRINT and READ

Each `PRINT` command iterates through the list of elements in the order they appear. Strings use `writes`, integers and logicals use `writei`, and reals use `writef`. At the end of every `PRINT`, a `writeln` is always emitted.

The VM's `READ` reads a string. Therefore, to read integers it is necessary to use:

```text
read
atoi
```

For reals, it would be used:

```text
read
atof
```

After conversion, the value is saved in the corresponding variable or array position.

### 7.8 IF, ELSE, DO, and GOTO

The VM does not have a high-level `if` instruction. Therefore, `IF` was translated using `jz`, `jump`, and automatically generated internal labels.

An `IF` without `ELSE` follows the pattern:

```text
<condition>
jz Lfim
<then code>
Lfim:
```

An `IF` with `ELSE` follows the pattern:

```text
<condition>
jz Lelse
<then code>
jump Lfim
Lelse:
<else code>
Lfim:
```

The `DO` loop was translated manually through initialization, condition, body, increment, and jump to the start:

```text
<start>
store var
Linicio:
var
<end>
infeq
jz Lfim
<body>
var
<step>
add
store var
jump Linicio
Lfim:
```

Fortran's numerical labels were converted deterministically to VM labels. For example, label `20` becomes `Lfortran20`. Thus, `GOTO 20` turns into:

```text
jump Lfortran20
```

### 7.9 Functions

Minimal support for functions was implemented to allow the conversion example. Function calls first push the arguments from left to right, then the function's address, and finally the call:

```text
<arg1>
<arg2>
pusha CONVRT
call
```

Inside the function, parameters are accessed with negative offsets relative to `fp`. Local variables and the return variable are reserved at the beginning of the function.

The function name inside the function itself is treated as a return variable. Thus, an instruction like:

```fortran
CONVRT = VAL
```

is treated as an assignment to `return_var`. When `RETURN` appears, the backend pushes this variable to the top of the stack and emits `return`:

```text
pushl <offset_return_var>
return
```

This convention made it possible to keep the behavior close to the Fortran style, but without implementing a complete subprogram system.

## 8. Tests Performed

Five test files were created in the `Testes/` folder, corresponding to the main examples in the assignment description.

| File | Test Objective | Constructs Validated |
|---|---|---|
| `ola.txt` | Minimal print program | `PROGRAM`, `PRINT`, string, `END` |
| `fatorial.txt` | Factorial calculation | `READ`, assignments, `DO`, multiplication, `PRINT` |
| `primo.txt` | Primality test | `LOGICAL`, `IF`, `AND`, `MOD`, `GOTO`, `ELSE` |
| `soma.txt` | Summing values in an array | arrays, `READ` for array, `NUMS(I)` access |
| `conversao.txt` | Decimal to bases 2 to 9 conversion | `INTEGER FUNCTION`, function call, parameters, `RETURN` |

These tests were chosen because they cover practically all relevant parts of the implementation. In particular, the `conversao.txt` example was important to validate the function calling convention, argument passing, local variables, and the return variable.

## 9. Main Difficulties Encountered

The first difficulty was the syntactic ambiguity of `ID(...)`. In Fortran, the same form can represent array access or a function call. Resolving this directly in the grammar would make the parser more confusing. The solution was to let the parser create a generic `Referencia` and resolve it later in the semantic analysis using the symbol table.

Another difficulty was translating arrays for the VM. Unlike scalar variables, an array requires address calculation. Furthermore, it was necessary to be careful with the fact that Fortran indices start at 1. Therefore, all array accesses make the `index - 1` adjustment before adding to the array base.

It was also necessary to carefully confirm the order of values on the stack. The VM calculates binary operations using the bottom value as the first operand and the top value as the second operand. This directly affects `sub`, `div`, comparisons, and `mod`. Therefore, the backend always generates the left expression first and only then the right one.

In functions, the most delicate part was understanding the calling convention. Arguments are pushed before the `call` and then become accessible at negative offsets relative to `fp`. Local variables, on the other hand, are at positive offsets after the initial `pushn` of the function. To keep the implementation simple, the return variable was treated as a special local variable.

Finally, there was also the decision not to add optimizations. This was a conscious choice: the goal was to generate correct and simple code, not to produce the shortest possible code.

## 10. How to Run the Compiler

The functioning of the main interface, `AnasinFortran.py`, was modified to use `stdin` or to perform batch processing of the tests folder.

To install dependencies:
```bash
python3 -m pip install ply
```

To run the compiler, there are two main approaches from the project root:

**Approach 1: Pipeline via Stdin**
The main script accepts input directly via `stdin`. This is very useful for piping files.
```bash
cd CompiladorFortran
python AnasinFortran.py < ../Testes/fatorial.txt
```

**Approach 2: Integrated Test Mode**
The compiler supports the `--test` (or `-t`) flag which automatically iterates over all files in the `Testes/` folder, compiling them and processing the results.
```bash
cd CompiladorFortran
python AnasinFortran.py -t
```

## 11. Conclusion

The work resulted in a simple compiler, but organized into clear phases. The compiler frontend handles reading, validation, and normalization of the Fortran program, while the backend is limited to traversing the validated AST and emitting virtual machine code.

The solution does not attempt to implement all of Fortran 77. Instead, it focuses on the subset necessary to fulfill the assignment and the provided examples. This approach made the project more manageable and reduced the likelihood of errors caused by extra features.

The most important parts of the implementation were the separation between parser and semantic analysis, resolving ambiguous references, managing scopes and offsets, calculating array addresses, and the minimal function calling convention. With these elements, it was possible to cover the five main examples of the project and mechanically generate VM code from the AST.
