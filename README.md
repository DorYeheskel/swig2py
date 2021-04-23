## swig2py: (Linux)
## What is it:
The tool purpose is to compile C/C++ code and convert it to python module, **during runtime**.
<br/>It is done by g++ compiler and [swig](http://www.swig.org/tutorial.html), using only 1 python script (less than 200 lines!).
<br/>It can be useful for learning purpose, improve performance, using low-level C code via python module, etc.

## Usage example:
## Example 1:
Define 2 functions in C and call them in your script:
```python
from swig2py import import_pkg

my_pkg = import_pkg("""
        int factorial(int n) {
            if(n > 1)
                return n * factorial(n - 1);
            return 1;
        }
        
        int sum(int a, int b) {
            return a+b;
        }
        
    """)
print(my_pkg.factorial(4))
print(my_pkg.sum(2, 4))
```
```bash
24
6 
```

## Example 2:
Define dummy function in C++, with std::vector and #include of external libs and call it in your script:
```python
from swig2py import import_pkg

my_pkg = import_pkg("""   
        #include <iostream>
        #include <vector> 

        void print_std_vector() {
            // Init vector:
            std::vector<int> vec = {1,2,3,4,5,6};

            // Print vector:             
            for (const auto& i : vec) {
                std::cout << i << ","; 
            }
            std::cout << std::endl;
        }

    """)
my_pkg.print_std_vector()
```
```bash
1,2,3,4,5,6,
```

## Example 3:
Using external cpp files:
```python
from swig2py import import_pkg

my_pkg = import_pkg(open(file='./my_api.cpp').read())
print(my_pkg.sum(2, 4))
```
```bash
6
```

## Example 4:
Compilation error:
```python
# File: my_script.py

from swig2py import import_pkg

try:
    my_pkg = import_pkg("""
        int sum(int a, int b) { @
            return a+b;
        }
        
    """)
    print(my_pkg.sum(2, 4))
except Exception as e:
    print('-E- Got error. See details below:')
    print(e)
```
```bash
> python my_script.py
```
``` 
-E- Got error. See details below:
Command : g++
Error   : \
pkg_curde8cb.h:2:37: error: stray ‘@’ in program
    2 |             int sum(int a, int b) { @
      |                                     ^
```

## How to install:
- git clone https://github.com/DorYeheskel/swig2py.git
- import swig2py to your script as in the examples above.
- Make sure that you have: python (> 3), swig, g++.
<br/> The three commands: **g++**, **swig**, **python3-config** (or python-config), must be defined in your current terminal, in order to use this tool 
<br/> (you can check it using the "which" build-in command)
<br/> Install if needed:
    - sudo apt-get install g++
    - sudo apt install swig
    - sudo apt install python python3-pip build-essential python3-dev 
  
## Notes:
This tool has some limitations, e.g compiling huge project may not work properly.
<br/>Moreover, swig can also transform other languages to Python modules (not only C/C++), 
<br/>which mean that you can covert Java or #C to Python modules, during runtime too. 
<br/>In the future, swig2py may have this kind of supports. 
<br/><br/>**Feel free to join and develop this project.**


