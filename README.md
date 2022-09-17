# trefunge-py

### What is Trefunge?

Trefunge is the 3D extension to the esoteric programming language [Befunge](http://esolangs.org/wiki/Befunge). As per Esolang's description:
>A Befunge program is laid out on a two-dimensional _playfield_ of fixed size. The playfield is a rectangular grid of ASCII characters, each generally representing an instruction. The playfield is initially loaded with the program.

It's a natural extension to add another dimension, and to do so, this interpreter implements the [Befunge-93 instruction set](https://esolangs.org/wiki/Befunge#Instructions), as well as two additional instructions:
- Zenith, represented by `z`: Go "up" a layer
- Nadir, represented by `n`: Go "down" a layer

### Program Definition
Aside from the two instructions, a layer is valid Befunge-93. Trefunge files use the extension of `.3f`, and since a program requires an unbounded amount of files, there are constraints places on the file names:

- All files representing a program are within a folder of whatever name you want
- File names must be integer-interpretable
- The file with name of `0` is always the initial layer
- Files prefixed with `_` are interpreted as negative (most OSes don't play nicely with files starting with a hyphen)
- Layers are sorted according to the integer interpretation of their name

The recommended program structure is something like this:
```
└── my_program
    ├── 0.3f
    ├── 10.3f
    ├── 20.3f
    ├── _10.3f
    └── _20.3f
```
This structure:
- Lets you define 0 as the "center" of your layers
- Gives you space to insert new layers in between existing layers without having to rename several files

### Usage
Running a program:
`python3 trefunge.py <path to folder containing your program files>`

Tests:
`pytest` at the root of this repo