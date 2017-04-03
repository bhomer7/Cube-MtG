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
DEBUG = True
# Future Concepts: Repeat block, standalone functions(append)


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
        self.card_list = defaultdict(dict)
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
                        self.card_list[rare_index(fname)][cur_line] = self.duplication
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
        added_vars = ['FileNames', '_master_card_list']
        variables['FileNames'] = self.file_names
        variables['_master_card_list'] = self.card_list
        # TODO Remove the used cards at the end

        for expr in self.exprs:
            expr.eval(pack)
        for variable in added_vars:
            del variables[variable]
        return pack


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
        pack.append(self.val.eval(pack))


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
        combined_card_list = []
        for _, lst in variables['_master_card_list'].items():
            combined_card_list += [k for k, v in lst.items() if v > 0]
        return combined_card_list


class ComprehensionNode(Node):
    def __init__(self, source, prop_list):
        self.source = source
        self.prop_list = prop_list

    def __str__(self):
        str_props = []
        for prop in self.prop_list:
            str_prop = str(prop)
            str_props.append('\n'.join('\t' + ln for ln in str_prop.split('\n')))
        res = "ComprehensionNode: " + str(self.source)
        res += '\n' + '\n'.join(str_props)
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
                if all(prop.eval(pack) for prop in self.prop_list):
                    res.append(x)
                for var in added_variables:
                    del variables[var]
        else:
            for x in lst:
                variables['X'] = x
                added_variables = ['X']
                if all(prop.eval(pack) for prop in self.prop_list):
                    res.append(x)
                for var in added_variables:
                    del variables[var]
        return res


class PropostionNode(Node):
    def __init__(self, fun, val1, val2):
        self.fun = fun
        self.val1 = val1
        self.val2 = val2

    def __str__(self):
        res = "PropositionNode: " + self.fun
        str_val1 = str(self.val1)
        res += '\n' + '\n'.join('\t' + ln for ln in str_val1.split('\n'))
        str_val2 = str(self.val2)
        res += '\n' + '\n'.join('\t' + ln for ln in str_val2.split('\n'))
        return res

    def __repr__(self):
        return str(self)

    def eval(self, pack):
        return propositions[self.fun](self.val1.eval(pack), self.val2.eval(pack))


def split_list(lst, *ids):
    for val, identifier in zip(lst, ids):
        variables[identifier] = val


def random_assign(lst, identifier):
    variables[identifier] = random.choice(lst)
    lst.remove(variables[identifier])


def update_variable(val, identifier):
    variables[identifier] = val


def rotate(lst, n):
    return lst[-n:] + lst[:-n]


def following(lst, val):
    return lst[(lst.index(val) + 1) % len(lst)]


def get_color(cd):
    res = get_color_identity(cd)
    return res


def get_list(fname):
    res = [k for k, v in variables['_master_card_list'][fname].items() if v > 0]
    return res


def concatenate(lst, val):
    return lst + val


def intersects(a, b):
    return len(set(a) & set(b)) > 0


def subset(a, b):
    return len(set(a) & set(b)) == len(a)


def contains_at_least(a, n):
    return len(a) >= n


functions = {
    'Rotate': rotate,
    'Zip': zip,
    'Following': following,
    'GetColors': get_color,
    'GetList': get_list,
    'Concatenate': concatenate
}
propositions = {
    'Intersects': intersects,
    'ContainsAtLeast': contains_at_least,
    'Subset': subset
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


def p_id_list(p):
    """id_list : ID
               | id_list COMMA ID
       val_listp : val
                 | val_listp COMMA val
       prop_list : prop
                 | prop_list AND prop"""
    if DEBUG:
        print(inspect.stack()[0][3])
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_val_list(p):
    """val_list : LBRACKET val_listp RBRACKET"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = p[2]


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
    """val : LBRACKET val WHERE prop_list RBRACKET"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = ComprehensionNode(AnyNode(), p[4])


def p_prop(p):
    """prop : PROPOSITION LPAREN val COMMA val RPAREN"""
    if DEBUG:
        print(inspect.stack()[0][3])
    p[0] = PropostionNode(p[1], p[3], p[5])


reserved = {
    'where': 'WHERE',
    'and': 'AND',
    'Add': 'ADD',
    'Any': 'ANY'
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
    'COMMENT'
) + tuple(set(reserved.values()))


@TOKEN(r'[a-zA-Z]+:')
def t_RARITY_NAME(tok):
    if DEBUG:
        print(inspect.stack()[0][3], tok)
    tok.value = tok.value[:-1]
    return tok


@TOKEN(r"'[^']*'")
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


@TOKEN(r'[a-zA-Z]+')
def t_ID(tok):
    if DEBUG:
        print(inspect.stack()[0][3], tok)
    if tok.value in reserved:
        tok.type = reserved[tok.value]
    print(tok)
    return tok


@TOKEN(r'/\*.*\*/')
def t_COMMENT(tok):
    if DEBUG:
        print(inspect.stack()[0][3], tok)


t_ASSIGN = '='
t_EXTRACT = '->'
t_SPLIT = '/>'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = ','
t_LPAREN = r'\('
t_RPAREN = r'\)'

t_ignore = ' \t'


# Error handling rule
def t_error(t):
    pass
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def p_error(p):
    if p:
        print("Syntax error at token", p.type, "line", p.lineno, p.lexpos)
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
    result = parser.parse(in_contents, lexer=lexer)
    return result
