# SPOL
### Symbolic Process Orientated Language

```
/*Spol Example*/
~print("Hello, World")
```


>Process-oriented programming is a programming paradigm that separates the concerns of data structures and the concurrent processes that act upon them. The data structures in this case are typically persistent, complex, and large scale - the subject of general purpose applications, as opposed to specialized processing of specialized data sets seen in high productivity applications (HPC). The model allows the creation of large scale applications that partially share common data sets. Programs are functionally decomposed into parallel processes that create and act upon logically shared data.
 
*[definition of process orientated programming from wikipedia](https://en.wikipedia.org/wiki/Process-oriented_programming)*
Spol is a process orientated language. That is the most I can surely say. Moving onto some more technical stuff to do with the language. The `symbolic` in the name refers to the syntax. Spol (mainly for my amusement) Uses symbols over keywords. So instead of writing "def" or "procedure" before defining processes, you'd instead type "£", and when returning values you write "->" instead of "return". So a program to calculate factorials(excluding modules, spol doesn't support those) in python3 would look like;
```python3
def exponent(a,b):
    c = 1
    while b > 0:
        c = c * a
        b = b - 1
    return c

print(exponent(2,5))
```
And in spol would look like;
```spol
£exponent[a,b]{
    c = 1
    b > 0 % {
        c = c * a
        b = b - 1
    }
    -> c
}
~print(~exponent(2,5))
/* python can't do this next thing */
~[£*~print(~exponent(2,8)),
  £*~print(~exponent(2,5)),
  £*~print(~exponent(2,2))]
```
You can see a much larger focus on symbols in spol. This makes the lacking structural rigidity in syntax less of an issue. Spol Is *built on python* though, most of the data it generates can be directly used by python. Eventually spol will be able to execute python bytecode, but for now it can't.

Spol also has a really simple variable scope, you have local and parent scope. "Global" scope is just whatever is in the local scope of the root process. Processes can have "links" between itself between itself and its parent. If a name is linked, then it will be manipulated in the parent nodes scope. Here's an example;

```spol
x = "hello"
y = "hi"

£demo*{ /* creates a parameterlaess process */
    x = "shw'mae"
    y = "su'mae"
    ~print(x) /* prints shw'mae */
    ~print(y) /* prints su'mae */
} [x]

~demo /* Invoke the process */

~print(x) /* prints shw'mae */
~print(y) /* prints hi */

```
So yep, That's all i can say about scope. I'm just going to provide some examples that covers most if not all of the syntax I can think of"

```spol
/*Process literals */
£process1* ~print("yeet") /* parameterless process that prints yeet */
£process2* {
    x = 100
    ~print(x)
} /* parameterless process that prints 100 */

£process3[x,y] -> x * x * y
£process4[x,y] {
    -> x * x * y
}

process5 = £*{} /* all process literals can be used in expressions, and they return the process object*/
```

```spol
/* Fun with lists */
_exp = [£[a]->1,
        £[a]->a,
        £[a]->a * a,
        £[a]->a * a * a,
        £[a]->a * a * a * a]

£exp[a,b]{ // 
    b <= 4 ? ->~_exp$b(a)
    : b > 0 ? {
        c = ~_exp$4(a)
        b = b - 4
        b > 0 % {
            c = c * a
            b = b - 1
        }
        -> c
    } : -> ¬ // return None
}
~print(~exp(5,3))
```

```spol
/*How a quirk in parameters being collected can change
  When a desired process is invoked [using process
  nesting to achieve concurrent parameter resolve]*/
£dp[x,d]{
    c = 1
    d > 0 % {
        c = c * x
        d = d - 1
    }
    -> c
}

~print("Concurrent resolve")

~[£*~print(~dp( 2,10)),
  £*~print(~dp( 2, 5)),
  £*~print(~dp( 2, 1))]

~print("\nSequencial resolve")

~[print(~dp( 2,10)),
  print(~dp( 2, 5)),
  print(~dp( 2, 1))]
```

```spol
/* implicit stack operator */
x = [1,2,3]
^x = x // x = [1,2,3,[...]] // or x where x[-1] is x
^^x = 4 // x = [1,2,3,4]
/*
The Implicit stack operator will either pop or push based
on context [push on assign, pop on collect]
The final line of this program pushes 4 onto whatever was 
popped from x
*/
```

```spol
/* List operators */
/* $ = index      */
/* # = length     */
x = [1,2,3]
~print(x$0) // 1
x$0 = #x
~print(x) // [3, 2, 3]
```

Spol also has classes. Though spol classes are python classes. This is due to spol building it's classes directly into python classes, because i was lazy. Though, methods are just spol code objects. Meaning only Spol derived classes can have methods invoked. It's syntax is `££name{attributes/methods}` with an optional `[classes which it derives from]` after. Spol also has a "class scope" when writing a class' method, you don't need to have "self" as a parameter, nor do you need to reference "this" or "self" for attributes. If a class has attribute x in a method you refer to it with `x`.
Spol currently doesn't have a full implementation of classes though. I won't provide examples of class definition here, because there's much more I need to implement for it to become Useful.