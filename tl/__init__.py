import functools
from .tlparse import tlParser

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
    ##
    ## CTL tree
    ##
    @translator
    def ctl (self) :
        return self("ctl", self)
    def _ctl (self, node) :
        return Phi(node.kind, *(self("ctl", child) for child in node.children), **node)
    def _ctl_name (self, node) :
        return Phi(node.kind, **node)
    def _ctl_bool (self, node) :
        return Phi(node.kind, **node)
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
        for child in node.children[0].children :
            assert child.kind not in "AEFGURX", f"cannot nest {child.kind} in A{node.children[0].kind}"
            assert not (child.actions or child.left_actions or child.right_actions), "actions not allowed"
        return Phi("A" + node.children[0].kind,
                   *(self("ctl", child) for child in node.children[0].children),
                   **node)
    def _ctl_E (self, node) :
        assert node.children[0].kind in "XFGUR", "E must be followed by X, F, G, U, or R"
        for child in node.children[0].children :
            assert child.kind not in "AEFGURX", f"cannot nest {child.kind} in E{node.children[0].kind}"
            assert not (child.actions or child.left_actions or child.right_actions), "actions not allowed"
        return Phi("E" + node.children[0].kind,
                   *(self("ctl", child) for child in node.children[0].children),
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
        assert node.children[0].kind not in "AEFGURX", f"cannot nest {node.children[0].kind} in X"
        return "X({})".format(self("its_ctl", node.children[0]))
    def _its_ctl_F (self, node) :
        assert not node.actions, "actions not allowed"
        assert node.children[0].kind not in "AEFGURX", f"cannot nest {node.children[0].kind} in F"
        return "F({})".format(self("its_ctl", node.children[0]))
    def _its_ctl_G (self, node) :
        assert not node.actions, "actions not allowed"
        assert node.children[0].kind not in "AEFGURX", f"cannot nest {node.children[0].kind} in G"
        return "G({})".format(self("its_ctl", node.children[0]))
    def _its_ctl_U (self, node) :
        assert not node.left_actions, "actions not allowed"
        assert not node.right_actions, "actions not allowed"
        assert node.children[0].kind not in "AEFGURX", f"cannot nest {node.children[0].kind} in U"
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
    def __init__ (self) :
        self.p = tlParser()
    def __call__ (self, source) :
        return self.p.parse(source, "start", semantics=self)
    _op = {"~" : "not",
           "&" : "and",
           "|" : "or",
           "=>" : "imply",
           "<=>" : "iff"}
    def phi (self, st) :
        """
        | "(" phi1:phi ")"
        | op:"~" phi1:phi
        | mod:quantifier phi1:phi
        | mod:unarymod phi1:phi
        | phi1:phi op:boolop phi2:phi
        | phi1:phi mod:binarymod phi2:phi
        | phi1:atom
        """
        if st.op is not None :
            return Phi(self._op[st.op], st.phi1, st.phi2)
        elif st.mod is not None :
            return Phi(st.mod.kind, st.phi1, st.phi2, **st.mod)
        else :
            return st.phi1
    def quantifier (self, st) :
        """
        op:/[AE]/ { "{" act:action "}" }
        """
        return Phi(st.op, actions=st.act)
    def unarymod (self, st) :
        """
        op:/[XFG]/ { "{" act:action "}" }
        """
        return Phi(st.op, actions=st.act)
    def binarymod (self, st) :
        """
        { "{" act1:action "}" } op:/[UR]/ { "{" act2:action "}" }
        """
        return Phi(st.op, left_actions=st.act1, right_actions=st.act2)
    def atom (self, st) :
        """
        /\w+|"\w+"|'\w+'/
        """
        if st in ("A", "E", "U", "R", "X", "F", "G",
                  "AX", "AF", "AG", "EX", "EF", "EG") :
            raise ValueError(f"variable {st} should be quoted")
        if st == "True" :
            return Phi("bool", value=True)
        elif st == "False" :
            return Phi("bool", value=False)
        else :
            return Phi("name", value=st.strip("\"'"), escaped=st[0] in "\"'")
    def actions (self, st) :
        """
        ",".{ { "~" } atom }
        """
        return [Phi(act.kind, *act.children, **act, neg=bool(sig)) for sig, act in st]

parse = Parser()
