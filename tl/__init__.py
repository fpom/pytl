"""Python parser and translator for varied temporal logics
"""

import functools
import re
from .tlparse import tlParser

version = "0.1"

def translator (method) :
    @functools.wraps(method)
    def wrapper (self) :
        try :
            return method(self)
        except AssertionError as err :
            raise ValueError(f"invalid {method.__name__} formula ({err})")
    return wrapper

class Phi (dict) :
    def __init__ (self, kind, *children, **attr) :
        super().__init__()
        self.kind = kind
        self.children = tuple(child for child in children if child is not None)
        for key, val in attr.items() :
            if val is not None :
                self[key] = val
    def __getattr__ (self, name) :
        return self.get(name, None)
    def __repr__ (self) :
        args = ", ".join([repr(self.kind)]
                         + [repr(c) for c in self.children]
                         + [f"{k}={v!r}" for k, v in self.items()])
        return f"{self.__class__.__name__}({args})"
    def __call__ (self, syntax, node) :
        try :
            handler = getattr(self, f"_{syntax}_{node.kind}")
            assert handler is not None, f"{node.kind!r} not accepted"
            return handler(node)
        except AssertionError as err :
            raise ValueError(f"invalid {syntax} formula ({err})")
    def __bool__(self):
      	return True
    ##
    ## CTL tree
    ##
    @translator
    def ctl (self) :
        return self("ctl", self)
    def _ctl (self, node) :
        return self.__class__(node.kind,
                              *(self("ctl", child) for child in node.children),
                              **node)
    def _ctl_name (self, node) :
        return self.__class__(node.kind, **node)
    def _ctl_bool (self, node) :
        return self.__class__(node.kind, **node)
    def _ctl_not (self, node) :
        return self._ctl(node)
    def _ctl_and (self, node) :
        return self._ctl(node)
    def _ctl_or (self, node) :
        return self._ctl(node)
    def _ctl_imply (self, node) :
        return self._ctl(node)
    def _ctl_iff (self, node) :
        return self._ctl(node)
    def _ctl_A (self, node) :
        assert node.children[0].kind in "XFGUR", "A must be followed by X, F, G, U, or R"
        assert not node.actions, "actions not allowed"
        assert not (node.children[0].actions or node.children[0].left_actions or node.children[0].right_actions), "actions not allowed"
        for child in node.children[0].children :
            assert child.kind not in "FGURX", f"cannot nest {child.kind} in A{node.children[0].kind}"
        return self.__class__("A" + node.children[0].kind,
                              *(self("ctl", child)
                                for child in node.children[0].children),
                              **node)
    def _ctl_E (self, node) :
        assert node.children[0].kind in "XFGUR", "E must be followed by X, F, G, U, or R"
        assert not node.actions, "actions not allowed"
        assert not (node.children[0].actions or node.children[0].left_actions or node.children[0].right_actions), "actions not allowed"
        for child in node.children[0].children :
            assert child.kind not in "FGURX", f"cannot nest {child.kind} in E{node.children[0].kind}"
        return self.__class__("E" + node.children[0].kind,
                              *(self("ctl", child)
                                for child in node.children[0].children),
                              **node)
    ##
    ## ARCTL tree
    ##
    @translator
    def arctl (self) :
        return self("arctl", self)
    def _arctl (self, node) :
        return self.__class__(node.kind,
                              *(self("arctl", child) for child in node.children),
                              **node)
    def _arctl_name (self, node) :
        return self.__class__(node.kind, **node)
    def _arctl_bool (self, node) :
        return self.__class__(node.kind, **node)
    def _arctl_not (self, node) :
        return self._arctl(node)
    def _arctl_and (self, node) :
        return self._arctl(node)
    def _arctl_or (self, node) :
        return self._arctl(node)
    def _arctl_imply (self, node) :
        return self._arctl(node)
    def _arctl_iff (self, node) :
        return self._arctl(node)
    def _arctl_A (self, node) :
        assert node.children[0].kind in "XFGUR", "A must be followed by X, F, G, U, or R"
        assert not (node.children[0].actions or node.children[0].left_actions or node.children[0].right_actions), "actions not allowed on temporal operators"
        for child in node.children[0].children :
            assert child.kind not in "FGURX", f"cannot nest {child.kind} in A{node.children[0].kind}"
        return self.__class__("A" + node.children[0].kind,
                              *(self("arctl", child)
                                for child in node.children[0].children),
                              **node)
    def _arctl_E (self, node) :
        assert node.children[0].kind in "XFGUR", "E must be followed by X, F, G, U, or R"
        assert not (node.children[0].actions or node.children[0].left_actions or node.children[0].right_actions), "actions not allowed on temporal operators"
        for child in node.children[0].children :
            assert child.kind not in "FGURX", f"cannot nest {child.kind} in E{node.children[0].kind}"
        return self.__class__("E" + node.children[0].kind,
                              *(self("arctl", child)
                                for child in node.children[0].children),
                              **node)
    ##
    ## ITS CTL syntax
    ##
    @translator
    def its_ctl (self) :
        return self("its_ctl", self) + ";"
    def _its_ctl_name (self, node) :
        if node.escaped :
            return '"{}"'.format(node.value)
        else :
            return '"{}=1"'.format(node.value)
    def _its_ctl_bool (self, node) :
        return str(node.value).lower()
    def _its_ctl_not (self, node) :
        return "!({})".format(self("its_ctl", node.children[0]))
    def _its_ctl_and (self, node) :
        return "({})&&({})".format(self("its_ctl", node.children[0]),
                                   self("its_ctl", node.children[1]))
    def _its_ctl_or (self, node) :
        return "({})||({})".format(self("its_ctl", node.children[0]),
                                   self("its_ctl", node.children[1]))
    def _its_ctl_imply (self, node) :
        return "({})->({})".format(self("its_ctl", node.children[0]),
                                   self("its_ctl", node.children[1]))
    def _its_ctl_iff (self, node) :
        return "({})<->({})".format(self("its_ctl", node.children[0]),
                                    self("its_ctl", node.children[1]))
    def _its_ctl_A (self, node) :
        assert node.children[0].kind in "XFGUE", "A must be followed by X, F, G, U, or R"
        assert not node.actions, "actions not allowed"
        return "A" + self("its_ctl", node.children[0])
    def _its_ctl_E (self, node) :
        assert node.children[0].kind in "XFGUE", "E must be followed by X, F, G, U, or R"
        assert not node.actions, "actions not allowed"
        return "E" + self("its_ctl", node.children[0])
    def _its_ctl_X (self, node) :
        assert not node.actions, "actions not allowed"
        assert node.children[0].kind not in "FGURX", f"cannot nest {node.children[0].kind} in X"
        return "X({})".format(self("its_ctl", node.children[0]))
    def _its_ctl_F (self, node) :
        assert not node.actions, "actions not allowed"
        assert node.children[0].kind not in "FGURX", f"cannot nest {node.children[0].kind} in F"
        return "F({})".format(self("its_ctl", node.children[0]))
    def _its_ctl_G (self, node) :
        assert not node.actions, "actions not allowed"
        assert node.children[0].kind not in "FGURX", f"cannot nest {node.children[0].kind} in G"
        return "G({})".format(self("its_ctl", node.children[0]))
    def _its_ctl_U (self, node) :
        assert not node.left_actions, "actions not allowed"
        assert not node.right_actions, "actions not allowed"
        assert node.children[0].kind not in "FGURX", f"cannot nest {node.children[0].kind} in U"
        return "(({})U({}))".format(self("its_ctl", node.children[0]),
                                    self("its_ctl", node.children[1]))
    def _its_ctl_R (self, node) :
        assert not node.left_actions, "actions not allowed"
        assert not node.right_actions, "actions not allowed"
        return "(({})R({}))".format(self("its_ctl", node.children[0]),
                                    self("its_ctl", node.children[1]))
    ##
    ## ITS LTL syntax
    ##
    @translator
    def its_ltl (self) :
        return self("its_ltl", self)
    def _its_ltl_name (self, node) :
        if node.escaped :
            return '"{}"'.format(node.value)
        else :
            return '"{}=1"'.format(node.value)
    def _its_ttl_bool (self, node) :
        return str(node.value).lower()
    def _its_ltl_not (self, node) :
        return "!({})".format(self("its_ltl", node.children[0]))
    def _its_ltl_and (self, node) :
        return "({})&&({})".format(self("its_ltl", node.children[0]),
                                   self("its_ltl", node.children[1]))
    def _its_ltl_or (self, node) :
        return "({})||({})".format(self("its_ltl", node.children[0]),
                                   self("its_ltl", node.children[1]))
    def _its_ltl_imply (self, node) :
        return "({})->({})".format(self("its_ltl", node.children[0]),
                                   self("its_ltl", node.children[1]))
    def _its_ltl_iff (self, node) :
        return "({})<->({})".format(self("its_ltl", node.children[0]),
                                    self("its_ltl", node.children[1]))
    def _its_ltl_X (self, node) :
        assert not node.actions, "actions not allowed"
        return "X" + self("its_ltl", node.children[0])
    def _its_ltl_F (self, node) :
        assert not node.actions, "actions not allowed"
        return "F" + self("its_ltl", node.children[0])
    def _its_ltl_G (self, node) :
        assert not node.actions, "actions not allowed"
        return "G" + self("its_ltl", node.children[0])
    def _its_ltl_U (self, node) :
        assert not node.left_actions, "actions not allowed"
        assert not node.right_actions, "actions not allowed"
        return "(({})U({}))".format(self("its_ltl", node.children[0]),
                                    self("its_ltl", node.children[1]))
    def _its_ltl_R (self, node) :
        assert not node.left_actions, "actions not allowed"
        assert not node.right_actions, "actions not allowed"
        return "(({})R({}))".format(self("its_ltl", node.children[0]),
                                    self("its_ltl", node.children[1]))

class Parser (object) :
    def __init__ (self, phiclass=Phi) :
        self.p = tlParser()
        self.c = phiclass
    def __call__ (self, source) :
        return self.p.parse(source, "start", semantics=self)
    _op = {"~" : "not",
           "&" : "and",
           "|" : "or",
           "=>" : "imply",
           "<=>" : "iff"}
    def start (self, st) :
        st.form["fair"] = st.fair
        return st.form
    def phi (self, st) :
        """
        | mod:quantifier phi1:phi
        | mod:unarymod phi1:phi
        | phi1:phi mod:binarymod phi2:phi
        """
        if st.phi2 is not None :
            return self.c(st.mod.kind, st.phi1, st.phi2, **st.mod)
        elif st.mod is not None :
            return self.c(st.mod.kind, st.phi1, **st.mod)
        else :
            return st.phi1
    def expr (self, st) :
        """
        | phi1:term op:boolop phi2:term
        | phi1:term
        """
        if st.op is not None :
            return self.c(self._op[st.op], st.phi1, st.phi2)
        else :
            return st.phi1
    def term (self, st) :
        """
        | phi1:atom
        | "(" phi1:phi ")"
        | op:"~" phi1:term
        """
        if st.op is not None :
            return self.c(self._op[st.op], st.phi1)
        else :
            return st.phi1
    def quantifier (self, st) :
        """
        op:/[AE]/ { "{" act:action "}" }
        """
        return self.c(st.op, actions=st.act)
    def unarymod (self, st) :
        """
        op:/[XFG]/ { "{" act:action "}" }
        """
        return self.c(st.op, actions=st.act)
    def binarymod (self, st) :
        """
        { "{" act1:action "}" } op:/[UR]/ { "{" act2:action "}" }
        """
        return self.c(st.op, left_actions=st.act1, right_actions=st.act2)
    def atom (self, st) :
        """
        /\w+|"\w+"|'\w+'/
        """
        if re.match('^([AE][XFG])|[AEXFGUR]$', st) :
            raise ValueError(f"variable {st} should be quoted")
        if st == "True" :
            return self.c("bool", value=True)
        elif st == "False" :
            return self.c("bool", value=False)
        else :
            return self.c("name", value=st.strip("\"'"), escaped=st[0] in "\"'")
    def actions (self, st) :
        """
        | "(" act1:actions ")"
		| op:"~" act1:actions
    	| act1:actions op:boolop act2:actions
		| act1:atom
        """
        if st.op is not None :
            return self.c(self._op[st.op], st.act1, st.act2)
        else :
            return st.act1

parse = Parser()
