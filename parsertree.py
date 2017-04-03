#!/usr/bin/env python3
import inspect
import random

import ply.yacc as yacc
import ply.lex as lex
from ply.lex import TOKEN

variables = {}


class Node():
    def eval(*args):
        return None


class RarityNode(Node):
    def __init__(self, name, exprs):
        self.name = name
        self.exprs = exprs
        # Add rarity_variables to variables dict

    def __str__(self):
        str_exprs = []
        for expr in self.exprs:
            str_expr = str(expr)
            str_exprs.append('\n'.join('\t' + ln for ln in str_expr.split('\n')))
        res = "RarityNode: " + self.name + '\n' + '\n'.join(str_exprs)
        return res

    def __repr__(self):
        return str(self)

    def eval(self, res, *args):
        for expr in self.exprs:
            res = expr.eval(res, *args)
        return res


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

    def eval(self, *args):
        return functions[self.fun](x.eval(*args) for x in self.args)


class AssignNode(Node):
    def __init__(self, fun, target, val):
        self.fun = fun
        self.target = target
        self.val = val

    def __str__(self):
        res = "AssignNode: " + self.fun.__name__ + ' ' + self.target
        str_val = str(self.val)
        res += '\n' + '\n'.join('\t' + ln for ln in str_val.split('\n'))
        return res

    def __repr__(self):
        return str(self)

    def eval(self, *args):
        return self.fun(self.target, self.val.eval())


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

    # TODO: Implement
    def eval(self, *args):
        return None


class IdNode(Node):
    def __init__(self, identifier):
        self.id = identifier

    def __str__(self):
        return "IdNode: " + self.id

    def __repr__(self):
        return str(self)

    def eval(self, *args):
        return variables[self.id]


class ConstantNode(Node):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "ConstantNode: " + self.value

    def __repr__(self):
        return str(self)

    def eval(self, *args):
        return self.value


class ComprehensionNode(Node):
    def __init__(self, identifier, prop_list):
        self.id = identifier
        self.prop_list = prop_list

    def __str__(self):
        str_props = []
        for prop in self.prop_list:
            str_prop = str(prop)
            str_props.append('\n'.join('\t' + ln for ln in str_prop.split('\n')))
        res = "ComprehensionNode: " + self.identifier
        res += '\n' + '\n'.join(str_props)
        return res

    def __repr__(self):
        return str(self)

    def eval(self, *args):
        lst = variables[self.id]
        for i, val in enumerate(lst):
            variables['X{}'.format(i)] = val
        variables['X'] = lst

        ret = [x for x in lst if all(prop.eval(*args) for prop in self.prop_list)]

        for i, _ in enumerate(lst):
            del variables['X{}'.format(i)]
        del variables['X']

        return ret


class PropostionNode(Node):
    def __init__(self, fun, val1, val2):
        self.fun = fun
        self.val1 = val1
        self.val2 = val2

    def __str__(self):
        res = "PropositionNode: " + self.fun.__name__
        str_val1 = str(self.val1)
        res += '\n' + '\n'.join('\t' + ln for ln in str_val1.split('\n'))
        str_val2 = str(self.val2)
        res += '\n' + '\n'.join('\t' + ln for ln in str_val2.split('\n'))
        return res

    def __repr__(self):
        return str(self)

    def eval(self, *args):
        return propositions[self.fun](self.val1.eval(*args), self.val2.eval(*args))


def split_list(lst, *args):
    for val, identifier in zip(lst, args):
        variables[identifier] = val


def rotate(lst, n):
    return lst[-n:] + lst[:-n]


def following(lst, val):
    return lst[(lst.index(val) + 1) % len(lst)]


# TODO: Implement
def get_color(cd):
    return []


# TODO: Implement
def get_list(fname):
    return []


def intersects(a, b):
    return len(set(a) & set(b)) > 0


def contains_at_least(a, n):
    return len(a) >= n


functions = {
    'Rotate': rotate,
    'Zip': zip,
    'Following': following,
    'GetColor': get_color,
    'GetList': get_list
}
propositions = {
    'Intersects': intersects,
    'ContainsAtLeast': contains_at_least
}


def p_rarity_list(p):
    """rarity_list : rarity
                   | rarity_list rarity"""
    print(inspect.stack()[0][3])
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_exprs_list(p):
    """exprs : expression
             | exprs expression"""
    print(inspect.stack()[0][3])
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_rarity(p):
    """rarity : RARITY_NAME exprs"""
    print(inspect.stack()[0][3])
    p[0] = RarityNode(p[1], p[2])


def p_assign_expression(p):
    """expression : ID ASSIGN val
                  | ID ASSIGN val_list"""
    print(inspect.stack()[0][3])
    p[0] = AssignNode(lambda x, y: variables.update((x, y)), p[1], p[3])


def p_extract_expression(p):
    """expression : val EXTRACT ID"""
    print(inspect.stack()[0][3])
    p[0] = AssignNode(lambda x, y: variables.update((x, random.choice(y))), p[3], p[1])


def p_split_expression(p):
    """expression : val SPLIT id_list"""
    print(inspect.stack()[0][3])
    p[0] = AssignNode(split_list, p[3], p[1])


def p_add_expression(p):
    """expression : ADD LPAREN val RPAREN"""
    print(inspect.stack()[0][3])
    p[0] = AddNode(p[3])


def p_id_list(p):
    """id_list : ID
               | id_list COMMA ID
       val_listp : val
                 | val_listp COMMA val
       prop_list : prop
                 | prop_list AND prop"""
    print(inspect.stack()[0][3])
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_val_list(p):
    """val_list : LBRACKET val_listp RBRACKET"""
    print(inspect.stack()[0][3])
    p[0] = p[2]


def p_val_id(p):
    """val : ID"""
    print(inspect.stack()[0][3])
    p[0] = IdNode(p[1])


def p_val_constant(p):
    """val : STRING
           | INTEGER"""
    print(inspect.stack()[0][3])
    p[0] = ConstantNode(p[1])


def p_val_function(p):
    """val : FUNCTION LPAREN val_listp RPAREN"""
    print(inspect.stack()[0][3])
    p[0] = FunctionNode(p[1], p[3])


def p_val_comprehension(p):
    """val : LBRACKET ID WHERE prop_list RBRACKET"""
    print(inspect.stack()[0][3])
    p[0] = ComprehensionNode(p[2], p[4])


def p_prop(p):
    """prop : PROPOSITION LPAREN val COMMA val RPAREN"""
    print(inspect.stack()[0][3])
    p[0] = PropostionNode(p[1], p[3], p[5])


reserved = {
    'where': 'WHERE',
    'and': 'AND',
    'Add': 'ADD'
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
    'RPAREN'
) + tuple(set(reserved.values()))


@TOKEN(r'[a-zA-Z]+:')
def t_RARITY_NAME(tok):
    print(inspect.stack()[0][3], tok.value)
    tok.value = tok.value[:-1]
    return tok


@TOKEN(r"'[^']*'")
def t_STRING(tok):
    print(inspect.stack()[0][3], tok.value)
    tok.value = tok.value[1:-1]
    return tok


@TOKEN(r'[0-9]+')
def t_INTEGER(tok):
    print(inspect.stack()[0][3], tok.value)
    tok.value = int(tok.value)
    return tok


@TOKEN(r'[a-zA-Z]+')
def t_ID(tok):
    print(inspect.stack()[0][3], tok.value)
    if tok.value in reserved:
        tok.type = reserved[tok.value]

    return tok


# @TOKEN('\ \\\t')
# def t_IGNORED(tok):
#     print(inspect.stack()[0][3], tok.value)
#     pass


t_ASSIGN = '='
t_EXTRACT = '->'
t_SPLIT = '/>'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = ','
t_LPAREN = r'\('
t_RPAREN = r'\)'

t_ignore = ' \t'
# import re
# print(re.search(r'(?m)^[(\ \ \ \ )\t]', 'test\n\tasdf'))


# Error handling rulr
def t_error(t):
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def p_error(p):
    if p:
        print("Syntax error at token", p.type, "line", p.lineno, p.lexpos)
        # Just discard the token and tell the parser it's okay.
        parser.errok()
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
