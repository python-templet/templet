# Python Templating

Here is a cute lightweight python templating module that supports inline python, speedy compilation, subtemplates, and subclassing, all with 70 lines of code.

Basic usage looks like this:

```
import templet

class PoemTemplate(templet.Template):
  template = "The $creature jumped over the $thing."

print PoemTemplate(creature='cow', thing='moon')
```

Template strings are compiled into methods through the magic of python metaclasses, so they run fast.

The class above actually becomes a class with a method called "template" that calls "write" several times. You can think of the class as being roughly equivalent to this:

```
class PoemTemplate(templet.Template):
  def template(self, creature=None, thing=None):
    self.write("The ")
    self.write(creature)
    self.write(" jumped over the ")
    self.write(thing)
    self.write(".")
```

Templates can contain `${...}` and `${{...}}` blocks with python code, so you are not limited to just variable substitution: you can use arbitrary python in your template. This straightforward approach of compiling a template into python is simple, yet powerful...

## Templates in Python

Why another python templating system?

Python's built-in string interpolation is great for little messages, but its lack of inline code makes the % operator too clumsy for building larger strings like HTML files. There are more than a dozen "full" templating solutions aimed at making it easy to build HTML in python, but they are all too full-featured for my taste.

For my weekend hacking projects, I don't really want to have to introduce a whole new language and install a big package just to build some strings. Why is it that Django and Cheetah call functions "filters" and make you register and invoke them with contortions like {{ var|foo:"bar" }} or ${var, foo="bar"}? Why do template systems invent their own versions of "if" and "while" and "def"? Python is a beautiful language, and I do not want to embed esperanto. I just want my templates to be python.

A few people have made simple python templates that avoid overcomplexity. For example, James Tauber has played with overriding getitem to make % itself more powerful. I like his idea, and I like the power you get when making each template into a class, but I find the % technique too clumsy in practice.

Tomer Filiba's lightweight Templite class is the solution I have seen that comes closest to exposing the simplicity of python in a lightweight template system. Wherever one of Filiba's templates is not literal text, it is python. Although Filiba does have his own template parser, he does not invent a new "if" statement or a new concept for function calls. I especially like the fact that Templite weighs in at just 40 lines of code with no dependencies.

But maybe Templite is just slightly too simple. When building the not-very-complicated UI for the RPS arena, I ended up rolling a new solution, because found that I wanted some key things that Templite misses:

 * Access to globals (like imported modules) from inline code.
 * Object-orientation: access to "self", method calls, inheritance, etc.
 * Nice handling of indented text and other help with long strings in code.
 * Load-time compilation (and friendly compilation errors).
 * Syntactic sugar for common simple $vars and ${expressions()}.
 * The python templet module here provides all these things by synthesizing Filiba's idea and Tauber's style, mixing in the magic of metaclasses.

## Keeping it Simple with Python Templets

The template language understands the following forms:

| syntax | meaning |
|-------|---------|
| `$myvar`	|	inserts the value of the variable 'myvar' |
| `${...}`	|	evaluates the expression and inserts the result |
| `${{...}}`	|	executes enclosed code; you can use `self.write(text)` to insert text |
| `$<sub_template>`	|	shorthand for `${{self.sub_template(vars())}}` |
| `$$`	|	an escape for a single $ |
| `$` (at the end of a line)	|	a line continuation |

Code in a template has access to 'self' and can take advantage of methods, members, base classes, etc., like normal code in a method. The method 'self.write(text)' inserts text into the template. And any class attribute ending with `_template` will be compiled into a subtemplate method that can be called from code or by using `$<...>`. Subtemplates are helpful for decomposing a template and when subclassing.

A longer example:

```
import templet, cgi

class RecipeTemplate(templet.Template):
  template = r'''
    <html><head><title>$dish</title></head>
    <body>
    $<header_template>
    $<body_template>
    </body></html>
    '''
  header_template = r'''
    <h1>${cgi.escape(dish)}</h1>
    '''
  body_template = r'''
    <ol>
    ${{
      for item in ingredients:
        self.write('<li>', item, '\n')
    }}
    </ol>
    '''
```

Notice that all the power of templets comes from python. To get HTML escaping, we just "import cgi" and call "cgi.escape()". To repeat things, we just use python's "for" loop. To make templates with holes that can be overridden, we just break up the template into multiple methods and use python inheritance. We could have added ordinary methods to the class and called them from the template as well. So writing a templet template is nothing special: we are just writing a python class.

RecipeTemplate can be expanded as follows:

```
print RecipeTemplate(dish='burger', ingredients=['bun', 'beef', 'lettuce'])
```

And it can be subclassed like this:

```
class RecipeWithPriceTemplate(RecipeTemplate):
  header_template = "<h1>${cgi.escape(dish)} - $$$price</h1>\n"
```

We get all the power and simplicity of python in our templates.

## The templet module

How does it work? The idea is simple. When a templet.Template subclass is defined, a metaclass processes the class definition, and all the "template" class member strings are chopped up and expanded into pieces of straight-line code.

When a template is instantiated, the main template() method is run and the written results are accumulated as a list of strings in "self.output". This list is concatenated when the instance is converted to a string.

