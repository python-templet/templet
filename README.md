# Python Templating with @templet

Here is an elegant lightweight python templating module that supports inline python, speedy compilation, subtemplates, and subclassing, all in a simple decorator module implemented in about 125 lines of python.

## What's New

Templet was created by David Bau, and modifications for version 4 are by Krisztián Fekete. Version 4 adds:

 * Python 3 support.
 * Proper unit tests, verifying python2, python3, and pypy support.
 * Support only unicode strings (no bytestrings).
 * Removed special case for empty-first-newline.
 * Cleaned up code for readability.

## Usage

To use templet, just annotate a python function with @templet, and then put the template text where the docstring would normally be. Leave the function body empty, and efficient code to concatenate the contents will be created.

```
  from templet import templet
  
  @templet
  def myTemplate(animal, body):
    "the $animal jumped over the $body."
  
  print(myTemplate('cow', 'moon'))
```

This is turned into something like this:

```
  def myTemplate(animal, body):
    out = []
    out.append("the ")
    out.append(str(animal))
    out.append(" jumped over the ")
    out.append(str(body))
    out.append(".")
    return ''.join(out)
```

There are just six constructs that are supported, all starting with $:

| syntax | meaning |
|--------|---------|
| `$myvar` | inserts the value of the variable `myvar` |
| `${...}` |  evaluates the expression and inserts the result |
| `${[...]}` |  runs a list comprehension and concatenates the results |
| `${{...}}` | executes enclosed code; use `out.append(text)` to insert text |
| `$$` | an escape for a single `$` |
| `$` | (at the end of the line) is a line continuation |

All ordinary uses of `$` in the template need to be escaped by doubling the `$$` - with the exception of (as mentioned above) `$.`, `$(`, `$/`, `$'`, and `$"`.

In the actual generated code, line numbers are aligned exactly so that both syntax errors and runtime errors in exception traces are reported on the correct line of the template file in which the code appears.

## Philosophy

The philosophy behind templet is to introduce only the concepts necessary to simplify the construction of long strings in python; and then to encourage all other logic to be expressed using ordinary python.

A @templet function can do everything that you can do with any function that returns a string: it can be called recursively; it can have variable or keyword arguments; it can be a member of a package or a method of a class; and it can access global imports or invoke other packages. As a result, although the construct is extremely simple, it brings all the power of python to templates, and the @templet idea scales very well.

Beyond simple interpolation, templet does not invent any new syntax for data formatting. If you want to format a floating-point number, you can write `${"%2.3f" % num}`; if you want to escape HTML sequences, just write `${cgi.escape(message)}`. Not as brief as a specialized syntax, but easy to remember, brief enough, and readable to any python programmer.

Similarly, templet does not invent any new control flow or looping structures. To loop a template, you need to use a python loop or list comprension and call the subtemplate as a function:

```
 @templet
 def doc_template(table):
   """\
   <body>
   <h1>${ table.name }</h1>
   <table>
   ${{
     for item in table:
       out.append(self.row_template(item))
   }}
   </table>
   </body>
   """
```

If you prefer list comprehensions, it is slightly more brief:

```
 @templet
 def doc_template(table):
   """\
   <body>
   <h1>${ table.name }</h1>
   <table>
   ${[self.row_template(item) for item in table]}
   </table>
   </body>
   """
```

The design encourages simple templates that read in straight-line fashion, an excellent practice in the long run. Although when invoking subtemplates you need to pass state, of course you can use @templet to make methods and pass state on "self", or use object parameters.

## Details and Style

Some tips/guidelines for using these annotations.

Whitespace can be important inside HTML, but for python readability you often want to indent things, so @templet gives you a few tools:

 * It identifies the number of leading spaces that are uniformly used to the left of the template and strips them.
 * It allows you to use a `$` at the end of a line for a line continuation.

So my recommended style for multiline templates is:

 * indent template text in the function as if it were python code.
 * use a python triple-quote and put the opening quote on its own line.
 * never indent HTML tags - they just get too deep, so put them all at column 0.
 * when nesting gets confusing, for readability, just put one tag on each line.
 * liberally use `$` continuations if layout demands no-whitespace.
 * indent code inside `${{` and then put `}}` on its own line (a newline right after a closing `}}` is eaten).

Relative indenting for python code inside `${{...}}` is preserved using the same leading-space-stripping trick as is used for the templates themselves, so you can indent embedded python as normal, and you can start the indenting at whichever column feels natural. I usually indent embedded python by one more level.

In the unusual case where it is necessary to emit text that has leading spaces on every line, you can begin the template with a continuation line with the `$` in the column that you want to treat as column zero, as follows:

```
@templet
def indented(x):
   """\
   $
      var val
      x   $x
   """
```

One question is whether the opening `"""` should be on the same line as the def or its own line. For clarity I usually put the opening quote on its own line, but to get columns to line up correctly, I eat the newline with a python line continuation immediately `"""\`.

For example, if you want to achieve all on one line the following:


```
<tr><td class="..."><a class="..." href="/foo/bar/...">....</a></td><td class="...">...</td></tr>
```

Then you could use:

```
@templet
def table_row(row_data):
  """\
  <tr>$
  <td class="${col1_class} def">$
  <a class="${link_class}"$
   href="/foo/bar/${cgi.escape(filename, True)}">$
  ${cgi.escape(link_text})}$
  </a>$
  </td>$
  <td class="${col2_class}">$
  ${{
    if (enrolled): out.append('enrolled')
  }}
  ${cgi.escape(label_text)}$
  </td>$
  </tr>
  """
```
