#!/usr/bin/env python3
import glob
import inspect
import random

from collections import defaultdict

import ply.yacc as yacc
import ply.lex as lex
from ply.lex import TOKEN

from gatherer import get_color_identity

variables = {}
DEBUG = False
# Future Concepts: Prevent duplicates in the same pack,
#                  Add Misc variable for remaining after all processing,
#                  Debug for printing results
#                  If blocks


def rare_index(r):
    """
    Split off the index into the config from a filename.
    """
    return r.split('/')[-1].split('.')[0]


class Node():
    def eval(*args):
        return None


class RarityListNode(Node):
    def __init__(self, lst):
        self.lst = lst

    def __str__(self):
        str_nodes = []
        for node in self.lst:
            str_node = str(node)
            str_nodes.append('\n'.join('\t' + ln for ln in str_node.split('\n')))
        return "RarityListNode:\n" + '\n'.join(str_nodes)

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        for node in self.lst:
            node.eval(pack)
        return True


class RarityNode(Node):
    def __init__(self, name, duplication, exprs):
        self.name = name
        self.exprs = exprs
        self.duplication = duplication
        self.file_list = defaultdict(list)
        self.card_list = {}
        self.file_names = glob.glob(name + '/*.dec')
        for fname in self.file_names:
            with open(fname) as rare_file:
                cur_line = ''
                comment = True
                for line in rare_file:
                    if comment:
                        cur_line = line
                    else:
                        cur_line += line
                        self.file_list[rare_index(fname)].append(cur_line)
                        self.card_list[cur_line] = self.duplication
                    comment = not comment
        self.file_names = [rare_index(f) for f in self.file_names]

    def __str__(self):
        str_exprs = []
        for expr in self.exprs:
            str_expr = str(expr)
            str_exprs.append('\n'.join('\t' + ln for ln in str_expr.split('\n')))
        res = "RarityNode: " + self.name + ' ' + str(self.duplication) + '\n' + '\n'.join(str_exprs)
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        added_vars = ['FileNames', '_master_card_list', '_master_file_list']
        variables['FileNames'] = self.file_names
        variables['_master_card_list'] = self.card_list
        variables['_master_file_list'] = self.file_list
        # TODO Remove the used cards at the end

        for expr in self.exprs:
            expr.eval(pack)
        for variable in added_vars:
            del variables[variable]
        return pack


class RepeatNode(Node):
    def __init__(self, n, exprs):
        self.n = n
        self.exprs = exprs

    def __str__(self):
        str_exprs = []
        for expr in self.exprs:
            str_expr = str(expr)
            str_exprs.append('\n'.join('\t' + ln for ln in str_expr.split('\n')))
        res = "RepeatNode: " + str(self.n) + '\n' + '\n'.join(str_exprs)
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        for _ in range(self.n):
            for expr in self.exprs:
                expr.eval(pack)
        return pack


class ListNode(Node):
    def __init__(self, vals):
        self.vals = vals

    def __str__(self):
        str_exprs = []
        for expr in self.vals:
            str_expr = str(expr)
            str_exprs.append('\n'.join('\t' + ln for ln in str_expr.split('\n')))
        res = "ListNode:\n" + '\n'.join(str_exprs)
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        return [x.eval(pack) for x in self.vals]


class FunctionNode(Node):
    def __init__(self, fun, args):
        self.fun = fun
        self.args = args

    def __str__(self):
        str_args = []
        for arg in self.args:
            str_arg = str(arg)
            str_args.append('\n'.join('\t' + ln for ln in str_arg.split('\n')))
        res = "FunctionNode: " + self.fun + '\n' + '\n'.join(str_args)
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        return functions[self.fun](*[x.eval(pack) for x in self.args])


class AssignNode(Node):
    def __init__(self, fun, val, *targets):
        self.fun = fun
        self.targets = targets
        self.val = val

    def __str__(self):
        res = "AssignNode: " + self.fun.__name__ + ' ' + str(self.targets)
        str_val = str(self.val)
        res += '\n' + '\n'.join('\t' + ln for ln in str_val.split('\n'))
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        return self.fun(self.val.eval(pack), *self.targets)


class AddNode(Node):
    def __init__(self, val):
        self.val = val

    def __str__(self):
        res = "AddNode:\n"
        str_val = str(self.val)
        res += '\n'.join('\t' + ln for ln in str_val.split('\n'))
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        res = self.val.eval(pack)
        if DEBUG:
            print('Adding', res)
        if res in pack:
            print('Double adding', res)
        pack.append(res)
        variables['_master_card_list'][res] -= 1


class IdNode(Node):
    def __init__(self, identifier):
        self.id = identifier

    def __str__(self):
        return "IdNode: " + self.id

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        return variables[self.id]


class ConstantNode(Node):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "ConstantNode: " + str(self.value)

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        return self.value


class AnyNode(Node):
    def __str__(self):
        return "AnyNode"

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        combined_card_list = [k for k, v in variables['_master_card_list'].items() if v > 0 and k not in pack]
        return combined_card_list


class ComprehensionNode(Node):
    def __init__(self, source, prop):
        self.source = source
        self.prop = prop

    def __str__(self):
        str_prop = '\n'.join('\t' + ln for ln in str(self.prop).split('\n'))
        res = "ComprehensionNode: " + str(self.source) + '\n' + str_prop
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        lst = self.source.eval(pack)
        if len(lst) == 0:
            return []
        res = []
        if isinstance(lst[0], (list, tuple)):
            for x in lst:
                added_variables = []
                for i, val in enumerate(x):
                    variables['X{}'.format(i)] = val
                    added_variables.append('X{}'.format(i))
                if self.prop.eval(pack):
                    res.append(x)
                for var in added_variables:
                    del variables[var]
        else:
            for x in lst:
                variables['X'] = x
                added_variables = ['X']
                if self.prop.eval(pack):
                    res.append(x)
                for var in added_variables:
                    del variables[var]
        return res


class PropositionNode(Node):
    def __init__(self, fun, *vals):
        self.fun = fun
        self.vals = vals

    def __str__(self):
        str_vals = []
        for val in self.vals:
            str_val = str(val)
            str_vals.append('\n'.join('\t' + ln for ln in str_val.split('\n')))
        res = "PropositionNode: " + self.fun + '\n' + '\n'.join(str_vals)
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        return propositions[self.fun](*(v.eval(pack) for v in self.vals))


def split_list(lst, *ids):
    if len(ids) < len(lst):
        print("Not splitting a large enough tuple")
    for val, identifier in zip(lst, ids):
        if identifier != '_':
            variables[identifier] = val


def random_assign(lst, identifier):
    if len(lst) == 0:
            raise ValueError("Empty list being extracted from")
    i = random.randint(0, len(lst) - 1)
    variables[identifier] = lst.pop(i)


def update_variable(val, identifier):
    variables[identifier] = val


def rotate(lst, n):
    return lst[-n:] + lst[:-n]


def following(lst, val):
    return lst[(lst.index(val) + 1) % len(lst)]


def get_color(cd):
    res = list(get_color_identity(cd))
    if 'Colorless' in res:
        res.remove('Colorless')
    return res


def zip_lists(*args):
    res = list(zip(*args))
    return res


def get_list(fname):
    res = [cd for cd in variables['_master_file_list'][fname] if variables['_master_card_list'][cd] > 0]
    return res


def concatenate(lst, val):
    return lst + val


def intersects(a, b):
    return len(set(a) & set(b)) > 0


def intersect(a, b):
    res = list(set(a) & set(b))
    return res


def subset(a, b):
    return len(set(a) & set(b)) == len(a)


def contains_at_least(a, n):
    return len(a) >= n


def contains_exact(a, n):
    return len(a) == n


def contains(a, *args):
    res = True
    for b in args:
        res &= b in a
    return res


def or_props(*args):
    if len(args) == 0:
        return False
    else:
        return args[0] or or_props(*args[1:])


def and_props(*args):
    if len(args) == 0:
        return True
    else:
        return args[0] and and_props(*args[1:])


def not_prop(p):
    return not p


def id_prop(p):
    return p


functions = {
    'Rotate': rotate,
    'Zip': zip_lists,
    'Following': following,
    'GetColors': get_color,
    'GetList': get_list,
    'Concat': concatenate,
    'Intersect': intersect
}
propositions = {
    'Intersects': intersects,
    'ContainsAtLeast': contains_at_least,
    'ContainsExact': contains_exact,
    'Contains': contains,
    'Subset': subset,
    'Or': or_props,
    'And': and_props,
    'Not': not_prop,
    'Id': id_prop
}


def p_start(p):
    """start : rarity_list"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = RarityListNode(p[1])


def p_rarity_list(p):
    """rarity_list : rarity
                   | rarity_list rarity"""
    if DEBUG:
        print(inspect.stack()[0][3])
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_exprs_list(p):
    """exprs : expression
             | exprs expression"""
    if DEBUG:
        print(inspect.stack()[0][3])
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_rarity(p):
    """rarity : RARITY_NAME INTEGER exprs"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = RarityNode(p[1], p[2], p[3])


def p_expression_repeat(p):
    """expression : REPEAT INTEGER LBRACE exprs RBRACE"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = RepeatNode(p[2], p[4])


def p_assign_expression(p):
    """expression : ID ASSIGN val
                  | ID ASSIGN val_list"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = AssignNode(update_variable, p[3], p[1])


def p_extract_expression(p):
    """expression : val EXTRACT ID"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = AssignNode(random_assign, p[1], p[3])


def p_split_expression(p):
    """expression : val SPLIT id_list"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = AssignNode(split_list, p[1], *p[3])


def p_add_expression(p):
    """expression : ADD LPAREN val RPAREN"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = AddNode(p[3])


def p_val_list(p):
    """val_list : LBRACKET val_listp RBRACKET"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = ListNode(p[2])


def p_val_id(p):
    """val : ID"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = IdNode(p[1])


def p_val_any(p):
    """val : ANY"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = AnyNode()


def p_val_constant(p):
    """val : STRING
           | INTEGER"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = ConstantNode(p[1])


def p_val_function(p):
    """val : FUNCTION LPAREN val_listp RPAREN"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = FunctionNode(p[1], p[3])


def p_val_comprehension(p):
    """val : LBRACKET val WHERE prop RBRACKET"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = ComprehensionNode(p[2], p[4])


def p_prop(p):
    """prop : PROPOSITION LPAREN val_listp RPAREN"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = PropositionNode(p[1], *p[3])


def p_prop_nested(p):
    """prop : LPAREN prop RPAREN"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = PropositionNode('Id', p[2])


def p_prop_not(p):
    """prop : NOT prop"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = PropositionNode('Not', p[2])


def p_prop_or(p):
    """prop : prop OR prop"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = PropositionNode('Or', p[1], p[3])


def p_prop_and(p):
    """prop : prop AND prop"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = PropositionNode('And', p[1], p[3])


def p_separator_list(p):
    """id_list : ID
               | id_list COMMA ID
       val_listp : val
                 | val_listp COMMA val"""
    if DEBUG:
        print(inspect.stack()[0][3])
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


reserved = {
    'where': 'WHERE',
    'and': 'AND',
    'Add': 'ADD',
    'Any': 'ANY',
    'Repeat': 'REPEAT',
    'or': 'OR',
    'not': 'NOT'
}
for function in functions:
    reserved[function] = 'FUNCTION'
for proposition in propositions:
    reserved[proposition] = 'PROPOSITION'

tokens = (
    'RARITY_NAME',
    'ID',
    'ASSIGN',
    'EXTRACT',
    'SPLIT',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'STRING',
    'INTEGER',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE'
) + tuple(set(reserved.values()))
precedence = (
    ('left', 'AND', 'OR'),
    ('right', 'NOT'),
)


@TOKEN(r'[a-zA-Z]+:')
def t_RARITY_NAME(tok):
    if DEBUG:
        print(inspect.stack()[0][3], tok)
    tok.value = tok.value[:-1]
    return tok


@TOKEN(r"('[^']*')|" + '("[^"]*")')
def t_STRING(tok):
    if DEBUG:
        print(inspect.stack()[0][3], tok)
    tok.value = tok.value[1:-1]
    return tok


@TOKEN(r'[0-9]+')
def t_INTEGER(tok):
    if DEBUG:
        print(inspect.stack()[0][3], tok)
    tok.value = int(tok.value)
    return tok


@TOKEN(r'[a-zA-Z_][a-zA-Z0-9_]*')
def t_ID(tok):
    if tok.value in reserved:
        tok.type = reserved[tok.value]
    if DEBUG:
        print(inspect.stack()[0][3], tok)
    return tok


# Define a rule so we can track line numbers
def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


t_ASSIGN = '='
t_EXTRACT = '->'
t_SPLIT = '/>'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_COMMA = ','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ignore_COMMENT = r'/\*.*\*/'

t_ignore = ' \t'


def find_column(token):
    last_cr = token.lexer.lexdata.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column


# Error handling rule
def t_error(t):
    pass
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def p_error(t):
    if t:
        print("Syntax error at token", t.type, "line", t.lineno, find_column(t))
        # Just discard the token and tell the parser it's okay.
        # parser.errok()
    else:
        print("Syntax error at EOF")


# Build the lexer
lexer = lex.lex()

# Build the parser
parser = yacc.yacc()


# ------- Input function
def create_tree(in_file):
    in_contents = ''
    with open(in_file) as in_file_obj:
        in_contents = in_file_obj.read()
    result = parser.parse(in_contents, lexer=lexer, debug=DEBUG)
    return result
