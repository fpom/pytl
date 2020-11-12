# Python parser and translator for varied temporal logics

`pytl` parses a temporal logic formula into an abstract syntax tree, and allows to translate it to the syntax expected by model-checking tools. The input syntax supports a very general temporal logic that encompasses CTL, LTL, CTL\*, ACTL, ARCTL, ATL, ATL\*, etc. The conformance to a particular syntax is checked when the formula is translated.

## Input syntax

The syntax of an input formula `phi` is as follows:

    phi ::= "(" phi ")"
         |  "~" phi
         |  quantifier phi
         |  unarymod phi
         |  phi boolop phi
         |  phi binarymod phi
         |  atom

    quantifier ::= ("A" | "E") ("{" actions "}")?
    
    unarymod ::= ("X" | "F" | "G") ("{" actions "}")?
    
    boolop ::= "&" | "|" | "=>" | "<=>"
    
    binarymod ::= ("{" actions "}")? ("U" | "R") ("{" actions "}")?
    
    atom ::= /\w+|"[^\"]+"|'[^\']+'/
    
    actions ::= "~"? atom ("," "~"? atom)*

Where `"..."` are literals, and `/.../` are Python regexps. Note that this grammar makes no distinction between path and state formulas, so that both can be parsed.

## Abstract Syntax Tree

The result of `tl.parse()` is an AST provided as an instance of class `Phi`. Its constructor is called as `Phi(kind, *children, **attributes)` and it behaves as a `dict` whose content is that of `attributes`. It has two attributes:

 - `kind` is the type of the node, that is can be
    - the name of an operator, quantifier or modality (eg, `A`, `and`, etc.)
    - `bool` if the atom was `True` or `False`, in which case its value is provided in attribute `value`
    - `name` if the atom was a name or a string (considered as an escaped name), in which case its value is provided in attribute `value` and another attribute `escaped` tells whether this atom was provided quoted of not
 - `children` is the tuple of sub-formulas
 - if actions have been provided in the input, they are stored in attribute `actions` for unary quantifiers and modalities, or `left_actions` and `right_actions` for binary modalities. Each action is a `Phi` instance for an atom with an additional attribute `neg` that tells whether the atom was negated of not

For example, `tl.parse("A{foo, ~bar, 'egg'} spam")` returns:

    Phi('A',
        Phi('name', value='spam', escaped=False),
        actions=[Phi('name', value='foo', escaped=False, neg=False),
                 Phi('name', value='bar', escaped=False, neg=True),
                 Phi('name', value='egg', escaped=True, neg=False)])

## Translating to a specific syntax

Class `Phi` has methods to translate a formula to a specific syntax. Doing so, the formula is checked to be valid w.r.t. the requested syntax.

### CTL

`Phi.ctl()` returns a new AST whose quantifiers have been collapsed with the following modality. For instance:

    >>> parse("AX spam")
    Phi('A', Phi('X', Phi('name', value='spam', escaped=False)))
    >>> parse("AX spam").ctl()
    Phi('AX', Phi('name', value='spam', escaped=False))

If the formula is not a valid CTL formula, an exception `ValueError` is raised. The syntax for CTL formulas is:

    phi ::= quantifier unarymod phi
         |  quantifier phi binarymod phi
         |  phi boolop phi
         |  "~" phi
         |  "(" phi ")"
         |  atom

With actions forbidden.

### ITS-tools CTL and LTL

`Phi.its_ctl()` returns a string that encodes a CTL formula into the syntax expected by tool `its-ctl`. Here also, the formula has to be valid CTL. The syntax for `its-ctl` is CTL with:

  - actions are not allowed
  - a trailing semi-colon is added
  - every sub-formula is enclosed into parentheses
  - `&` is translated to `&&`
  - `|` is translated to `||`
  - `~` is translated to `!`
  - `=>` is translated to `->`
  - `<=>` is translated to `<->`
  - Boolean values are `true` and `false`
  - atoms are written as `"V=1"` is they were not quoted, or `"V"` is they were quoted

`Phi.its_ltl()` returns a string that encodes a LTL formula into the syntax expected by tool `its-ltl`. The formula has to be valid LTL. The syntax for `its-ltl` is as the general syntax without any quantifier nor actions. Then, operators, modalities, Boolean values, and atoms are translated as for `its-ctl`.

## Adding more translations

Class `Phi` provides the basic mechanism to write new translations. Say we want a translation to a syntax `xtl`, we shall add:

 - a method `Phi.xtl(self)` decorated with `@translator` that returns `self("xtl", self)`
 - for each kind `foo` of node that should be translated, a method `Phi._xtl_foo(self, node)` that translates a `node` whose kind is `foo`
 - missing methods will yield a translation error (eg, there is no method `Phi._its_ltl_A` because `A` is forbidden in `its_ltl`)
 - additional checks can be performed within each method using `assert`s whose error messages will be reused in the translation error message

See `tl/__init__.py` for more details.

Adding these methods can be made on the original code (don't hesitate to send a pull request), or by subclassing `Phi`. In the latter case, one has to build a new `parse` function using `myparse = tl.Parser(MyPhi)` so that it returns an instance of the new class `MyPhi`.

## Licence

`pytl` is (C) 2020 Franck Pommereau <franck.pommereau@univ-evry.fr>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
