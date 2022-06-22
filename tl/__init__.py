"""Python parser and translator for varied temporal logics
"""

import functools, re
from .tlparse import Lark_StandAlone, Transformer, v_args, Token

version = "0.2"

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
    def __iter__ (self) :
        yield self
        for child in self.children :
            yield from child
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
        assert node.children[0].kind in "XFGURWM", "A must be followed by X, F, G, U, R, W, or M"
        assert not node.actions, "actions not allowed"
        assert not (node.children[0].actions or node.children[0].left_actions or node.children[0].right_actions), "actions not allowed"
        for child in node.children[0].children :
            assert child.kind not in "FGURXWM", f"cannot nest {child.kind} in A{node.children[0].kind}"
        return self.__class__("A" + node.children[0].kind,
                              *(self("ctl", child)
                                for child in node.children[0].children),
                              **node)
    def _ctl_E (self, node) :
        assert node.children[0].kind in "XFGURWM", "E must be followed by X, F, G, U, R, W, or M"
        assert not node.actions, "actions not allowed"
        assert not (node.children[0].actions or node.children[0].left_actions or node.children[0].right_actions), "actions not allowed"
        for child in node.children[0].children :
            assert child.kind not in "FGURXWM", f"cannot nest {child.kind} in E{node.children[0].kind}"
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
        assert node.children[0].kind in "XFGURWM", "A must be followed by X, F, G, U, R, W, or M"
        assert not (node.children[0].actions or node.children[0].left_actions or node.children[0].right_actions), "actions not allowed on temporal operators"
        for child in node.children[0].children :
            assert child.kind not in "FGURXWM", f"cannot nest {child.kind} in A{node.children[0].kind}"
        return self.__class__("A" + node.children[0].kind,
                              *(self("arctl", child)
                                for child in node.children[0].children),
                              **node)
    def _arctl_E (self, node) :
        assert node.children[0].kind in "XFGURWM", "E must be followed by X, F, G, U, R, W, or M"
        assert not (node.children[0].actions or node.children[0].left_actions or node.children[0].right_actions), "actions not allowed on temporal operators"
        for child in node.children[0].children :
            assert child.kind not in "FGURXWM", f"cannot nest {child.kind} in E{node.children[0].kind}"
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
        return "&&".join("({})".format(self("its_ctl", child))
                         for child in node.children)
    def _its_ctl_or (self, node) :
        return "||".join("({})".format(self("its_ctl", child))
                         for child in node.children)
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
        # FIXME? remove A/E when it's the top-most quantifier
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
        return "&&".join("({})".format(self("its_ltl", child))
                         for child in node.children)
    def _its_ltl_or (self, node) :
        return "||".join("({})".format(self("its_ltl", child))
                         for child in node.children)
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

@v_args(inline=True)
class PhiTransformer (Transformer) :
    c = Phi
    def start (self, restr, main) :
        if restr is not None :
            for node in main :
                if not isinstance(node, self.c) :
                    continue
                if node.kind in ("A", "E") :
                    if restr.actions is not None :
                        assert node.actions is None, "cannot propagate global action restriction to an already restricted modality"
                        node["actions"] = restr.actions
                    for fair in restr.fairness :
                        getattr(node, fair.kind).append(fair)
        return main
    _not_atom = re.compile("^[AEXFGURWM]+$")
    def atom (self, token) :
        value = token.value
        if self._not_atom.match(value) :
            raise ValueError(f"variable {value} should be quoted")
        if value == "True" :
            return self.c("bool", value=True)
        elif value == "False" :
            return self.c("bool", value=False)
        elif value[0] in ("'", '"') :
            return self.c("name", value=value[1:-1], escaped=True)
        else :
            return self.c("name", value=value, escaped=False)
    def nop (self, child) :
        return child
    def not_op (self, phi) :
        return self.c("not", phi)
    _op = {"&" : "and",
           "|" : "or",
           "=>" : "imply",
           "<=>" : "iff"}
    def bin_op (self, first, *rest) :
        if not rest :
            return first
        assert all(op.value == rest[0].value for op in
                   rest[::2]), "cannot chain distinct Boolean operators"
        return self.c(self._op[rest[0].value], first, *rest[1::2])
    def mod (self, *items) :
        # phi : (UMOD [restrict])* sub [BMOD [act] sub]
        if items[-1] is not None :
            *items, left, mod, act, right = items
            form = self.c(mod.value, left, right,
                          actions=act)
        else :
            *items, form, _ = items
        quant = []
        for q in items :
            if isinstance(q, Token) :
                quant.extend(self.c(v, ufair=[], wfair=[], sfair=[]) for v in q.value)
            elif q is not None :
                quant[-1]["actions"] = q.actions
                for fair in q.fairness :
                    assert quant[-1].kind in "EA", f"cannot have fairness on {quant[-1].kind}"
                    getattr(quant[-1], fair.kind).append(fair)
        for q in reversed(quant) :
            q.children = (form,)
            form = q
        return form
    def act (self, *items) :
        return self.c("actions", self.bin_op(*items))
    def restrict (self, *items) :
        # restrict : (act | fair)+
        form = self.c("restrict", actions=[], fairness=[])
        for i in items :
            if i.kind == "actions" :
                form.actions.append(i)
            else :
                form.fairness.append(i)
        if not form.actions :
            form.actions = None
        elif len(form.actions) == 1 :
            form.actions = form.actions[0].children[0]
        else :
            assert False, "multiple action formulas not allowed"
        return form
    def fair (self, *items) :
        # fair : "[" FAIR (act | bool) [THEN (act | bool)] "]"  -> fair
        fair, *rest = items
        if rest[-1] is None :
            cond, then = None, rest[0]
        else :
            cond, _, then = rest
        if fair != "UFAIR" and cond is None :
            if then.kind == "actions" :
                cond = self.c("E", self.c("X", "True"), actions=[then])
            else :
                assert False, f"{fair} must have a condition or apply on an action"
        return self.c(fair.lower(),
                      condition=cond,
                      then=then)

def parse (form, phiclass=Phi) :
    class _Transformer (PhiTransformer) :
        c = phiclass
    parser = Lark_StandAlone(transformer=_Transformer())
    return parser.parse(form)
