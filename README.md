# SPOL
Symbolic Process Orientated Language
### intro
This isn't a serious language, Just what came out of me Learning BNF and wanting to practice building parsers. Anyway, SPOL is a occam inspired programming language. It breaks a script into a sequence of processes and then executes them sequencially. you can also execute processes concurrently.

####  _quick example_
```
£exp[a,b] {
	c =1
	b > 0 % {
		c = c * a
		b = b - 1
	}
	print c
}

~[exp(2,5),
    exp(2,3),
	exp(2,0),
	£*print "yeet"]
```
The program above calculates exponents, it defines a process `exp` which takes two parameters and prints the result of `a^b`, then it executes this process three times with varying parameters concurrently with a print statement. Everything ends up being printed in reverse order to how they were presented due to being sorted longest runtime to shortest runtime.
To run this (in the python shell atleast) just load the core script in IDLE and then type the command
```python
run("""
£exp[a,b] {
	c =1
	b > 0 % {
		c = c * a
		b = b - 1
	}
	print c
}

~[exp(2,5),
    exp(2,3),
	exp(2,0),
	£*print "yeet"]
""",genv)
```


------------

Don't Expect this Repository to be updated that often.
