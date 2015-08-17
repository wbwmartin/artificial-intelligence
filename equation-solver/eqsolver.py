#!/usr/bin/python
import eqparser
import math

trianglefunc = {
    'sin'   : 'arcsin',
    'cos'   : 'arccos',
    'tan'   : 'arctan',
    'arcsin': 'sin',
    'arccos': 'cos',
    'arctan': 'tan'
    }

opdict = {
    '+' : {'+', '-'},
    '-' : {'+', '-'},
    '*' : {'*', '/'},
    '/' : {'*', '/'}
    }

opdict2 = {
    '+' : '-',
    '-' : '+',
    '*' : '/',
    '/' : '*'
    }

numSet = {'FLOAT', 'INT'}
varSet = {'SYMBOL', 'VARIABLENAME'}

LOOP_NUM = 10



# Given a parser of an expression in tree form, find the goal variable,
# and locate the path from the root. It returns a list to record the path.

def findx(parser, var):
    if parser.leaf == var:
        return [parser]
    if parser.children == [ ]:
        return None
    if (parser.type == "EQUALS") or (parser.type == "BINARYOP"):
        fd0 = findx(parser.children[0], var)
        if not fd0:
            fd1 = findx(parser.children[1], var)
            if not fd1:
                return None
            else:
                return [parser] + fd1
        else:
            return [parser] + fd0
    else:
        fd = findx(parser.children, var)
        if not fd:
            return None
        else:
            return [parser] + fd



# Switch the two side of the root of a tree, and return the tree.

def switchSide(tree):
    temp = tree.children[0]
    tree.children[0] = tree.children[1]
    tree.children[1] = temp
    return tree



# Given a two-level subtree, find whether the child is on the left side, right
# side, or right below its parent. It returns an integer to represent the location.

def findLoc(parent, child):
    if parent.type == 'BINARYOP':
        if child == parent.children[0]:
            return 0
        if child == parent.children[1]:
            return 1
    if parent.type == 'UNARYOP' or parent.type == 'UNARYFUNCTION':
        return 2
    return -1



# Given a tree parser with the '=' on the top, move its child one step to make
# the goal variable one step closer to the solution. It returns a new tree parser.

def buildTree(p, loc):
    global numSet, varSet
    checkleaf = p.children[0].leaf

    # Cases for binary operations when goal variable is on the left side.
    if loc == 0:
        pstay = p.children[0].children[0]
        pmove = p.children[0].children[1]

        if checkleaf == '+':
            pright = eqparser.Node('BINARYOP', [p.children[1], pmove], '-')
        
        if checkleaf == '-':
            pright = eqparser.Node('BINARYOP', [p.children[1], pmove], '+')

        if checkleaf == '*':
            pright = eqparser.Node('BINARYOP', [p.children[1], pmove], '/')
            
        if checkleaf == '/':
            pright = eqparser.Node('BINARYOP', [p.children[1], pmove], '*')

        if checkleaf == '^':
            node1 = eqparser.Node('INT', None, 1)
            index = eqparser.Node('BINARYOP', [node1, pmove], '/')
            pright = eqparser.Node('BINARYOP', [p.children[1], index], '^')
            
        return eqparser.Node('EQUALS', [pstay, pright], '=')

    # Cases for binary operations when goal variable is on the right side.
    if loc == 1:
        pstay = p.children[0].children[1]
        pmove = p.children[0].children[0]

        if checkleaf == '+':
            pright = eqparser.Node('BINARYOP', [p.children[1], pmove], '-')
        
        if checkleaf == '-':
            pright = eqparser.Node('BINARYOP', [pmove, p.children[1]], '-')

        if checkleaf == '*':
            pright = eqparser.Node('BINARYOP', [p.children[1], pmove], '/')
            
        if checkleaf == '/':
            pright = eqparser.Node('BINARYOP', [pmove, p.children[1]], '/')

        if checkleaf == '^':
            nom = eqparser.Node('UNARYFUNCTION', p.children[1], 'log')
            den = eqparser.Node('UNARYFUNCTION', pmove, 'log')
            pright = eqparser.Node('BINARYOP', [nom, den], '/')
            
        return eqparser.Node('EQUALS', [pstay, pright], '=')

    # Cases for unary operations and unary functions.
    if loc == 2:
        if checkleaf == '-':
            pright = eqparser.Node('UNARYOP', p.children[1], '-')
        
        if checkleaf == 'log':
            node10 = eqparser.Node('INT', None, 10)
            pright = eqparser.Node('BINARYOP', [node10, p.children[1]], '^')

        if checkleaf == 'ln':
            nodeE = eqparser.Node('SYMBOL', None, 'e')
            pright = eqparser.Node('BINARYOP', [nodeE, p.children[1]], '^')
    
        if checkleaf == 'sqrt':
            node2 = eqparser.Node('INT', None, 2)
            pright = eqparser.Node('BINARYOP', [p.children[1], node2], '^')

        if checkleaf in trianglefunc.keys():
            pright = eqparser.Node('UNARYFUNCTION', p.children[1], trianglefunc[checkleaf])
            
        return eqparser.Node('EQUALS', [p.children[0].children, pright], '=')
        
    return None       



# Given a list of tree, change its form to the goal state with the goal variable
# on one side, e.g. "x = (3 - 1) / 2".

def goalTree(treeList):
    global newTree
    for i in range(len(treeList)-2):
        newTree = buildTree(newTree, findLoc(treeList[i+1], treeList[i+2]))



# Represent a tree in string form, excluding the color stuff.

def treeRepr(tree):
    return str(tree.children[0].leaf) + tree.leaf + str(tree.children[1].leaf)



# Four basic rules applied. (1) If the children of a tree are numbers, calculate.
# (2) If the children are both symbol or variable, and they are the same, then
# change the representing way, e.g. "a + a" -> "2 * a", "b / b" -> 1. (3) Special
# cases are considered, e.g. "a / 0"-> "undefined". "arcsin(2)" -> "undefined".

def baseRule(tree):
    global numSet, varSet
    if tree.children == [ ]:
        return tree
    
    tree = commRule(tree)
        
    if tree.type == 'UNARYFUNCTION':       
        if tree.children.type in numSet:
            if tree.leaf == 'log':
                return eqparser.Node('FLOAT', None, math.log10(tree.children.leaf))
            elif tree.leaf == 'ln':
                return eqparser.Node('FLOAT', None, math.log(tree.children.leaf))
            elif tree.leaf == 'sin' or tree.leaf == 'cos' or tree.leaf == 'tan':
                val = eval('math.' + tree.leaf + '(' + str(tree.children.leaf) + ')')
                return eqparser.Node('FLOAT', None, val)
            else:
                if tree.leaf == 'arcsin' or tree.leaf == 'arccos':
                    if tree.children.leaf > 1 or tree.children.leaf < -1:
                        return eqparser.Node('VARIABLENAME', None, 'undefined')
                val = eval('math.' + tree.leaf[0] + tree.leaf[3:] + '(' + str(tree.children.leaf) + ')')
                print val
                return eqparser.Node('FLOAT', None, val)
        
    if tree.type == 'UNARYOP':
        if tree.children.type in numSet:           
            return eqparser.Node(tree.children.type, None, 0 - tree.children.leaf)
        if tree.children.type in varSet:
            return eqparser.Node(tree.children.type, None, '(-' + tree.children.leaf + ')')
    if tree.type == 'BINARYOP':
        if tree.leaf == '/' and tree.children[1].leaf == 0:
            return eqparser.Node('VARIABLENAME', None, 'undefined')
        if tree.children[0].type in numSet and tree.children[1].type in numSet:
            if tree.leaf == '/':
                tree.children[1] = eqparser.Node('FLOAT', tree.children[1].children, float(tree.children[1].leaf))           
            if tree.leaf == '^':
                if tree.children[1].leaf == 1:
                    return tree.children[0]
                val = eval(str(tree.children[0].leaf) + '**' + str(tree.children[1].leaf))
            else:
                val = eval(treeRepr(tree))
            if type(val) is int:
                return eqparser.Node('INT', None, val)
            else:
                return eqparser.Node('FLOAT', None, val)

        if (tree.children[0].leaf == 0 and tree.leaf == '+'
            or tree.children[0].leaf == 1 and tree.leaf == '*'):
            return tree.children[1]
        
        if tree.children[0].leaf == 0 and tree.children[1].type in varSet and tree.leaf == '-':
            return eqparser.Node('VARIABLENAME', None, '(-' + tree.children[1].leaf + ')')
        
        if tree.children[0].type in varSet and tree.children[0].leaf == tree.children[1].leaf:
            if tree.leaf == '+':
                tree.leaf = '*'
                tree.children[0] = eqparser.Node('INT', None, 2)
                return tree
            if tree.leaf == '-':
                return eqparser.Node('INT', None, 0)
            if tree.leaf == '*':
                tree.leaf = '^'
                tree.children[1] = eqparser.Node('INT', None, 2)
                return tree
            if tree.leaf == '/':
                return eqparser.Node('INT', None, 1)

        if tree.children[0].type in varSet and tree.children[1].type in varSet:
            var = '(' + tree.children[0].leaf + ' ' + tree.leaf + ' ' + tree.children[1].leaf + ')'
            return eqparser.Node('VARIABLENAME', None, var)

        return commRule(tree)
    return tree



# The commutativity rule is applied, following the precedence from left to right:
# numbers, variables/symbols, child nodes. e.g. "c + 5" -> "5 + c",
# "(3 + a) * b" -> "b * (3 + a)".
 
def commRule(tree):
    if tree.leaf in {'+', '*'}:
        if tree.children[0].children != [ ] and tree.children[1].children == [ ]:
            switchSide(tree)
        if tree.children[0].children == [ ] and tree.children[1].children == [ ]:
            if tree.children[0].leaf > tree.children[1].leaf:
                switchSide(tree)
    return tree



# Iteration to simplify the tree through the basic rules.

def simpTree(tree):    
    if tree.leaf == 'e':
        return eqparser.Node('FLOAT', None, math.e)
    if tree.leaf == 'pi':
        return eqparser.Node('FLOAT', None, math.pi)
    
    if tree.children == [ ] or tree.leaf == 'undefined':
        return tree
    else:
        tree = baseRule(tree)
        if tree.type == 'BINARYOP':
            temp = eqparser.Node(tree.type, [simpTree(tree.children[0]), simpTree(tree.children[1])], tree.leaf)
            return baseRule(temp)
        else:
            return tree                      
        if tree.type == 'UNARYFUNCTION':
            temp = eqparser.Node(tree.type, simpTree(tree.children), tree.leaf)
            return baseRule(temp)
        else:
            return tree
            

 
# Heuristic -- Iterator to estimate the minimum future costs.

def estmHeu(tree):
    global heu
    if tree.children == [ ]:
        return tree.leaf
    if tree.type == 'BINARYOP':
        heu += 2
        estmHeu(tree.children[0])
        estmHeu(tree.children[1])
    elif tree.type == 'UNARYOP' or tree.type == 'UNARYFUNCTION':
        heu += 1
        estmHeu(tree.children)
    return None



# Iterator to find all the leaf of the tree.

def findLeaf(tree):
    global index
    sum = 0
    if tree.type == 'BINARYOP':
        if tree.children[0].children == [ ] and tree.children[1].children == [ ]:
            index -= 1
            sum += 1
    if tree.type == 'UNARY' or tree.type == 'UNARYFUNCTION':
        if tree.children.children == [ ]:
            index -= 1
            sum += 1
            
    if (index == 0):
        return [tree]
    
    elif tree.type == 'BINARYOP':
        fd0 = findLeaf(tree.children[0])
        fd1 = findLeaf(tree.children[1])        
        if fd0:
            return fd0 + [tree]
        if fd1:
            return fd1 + [tree]
        return None           
                
    elif tree.type == 'UNARY' or tree.type == 'UNARYFUNCTION':        
        fd = findLeaf(tree.children)
        if fd:
            return fd + [tree]
        return None



# The associativity rule is applied. It follows the process of A* tree and makes
# smart decisions.

def assoTree(ls):
    global opdict, opdict2, numSet, varSet, heu
    ch = ls[0]
    pa = ls[1]
    if pa.leaf == '+' and ch.leaf in opdict['+'] or pa.leaf == '*' and ch.leaf in opdict['*']:
        if pa.children[0].type in numSet or pa.children[0].type in varSet:
            ch1 = eqparser.Node('BINARYOP', [pa.children[0], pa.children[1].children[1]], ch.leaf)
            pa1 = eqparser.Node('BINARYOP', [pa.children[1].children[0], ch1], pa.leaf)
            pa1 = simpTree(pa1)
            heu = 0
            estmHeu(pa1)
            formula1 = 2 + heu
            ch2 = eqparser.Node('BINARYOP', [pa.children[0], pa.children[1].children[0]], pa.leaf)
            pa2 = eqparser.Node('BINARYOP', [ch2, pa.children[1].children[1]], ch.leaf)
            pa2 = simpTree(pa2)
            heu = 0
            estmHeu(pa2)
            formula2 = 2 + heu
            return pa1 if formula1 < formula2 else pa2
        
    if pa.leaf == '-' and ch.leaf in opdict['-'] or pa.leaf == '/' and ch.leaf in opdict['/']:
        if pa.children[0].type in numSet or pa.children[0].type in varSet:
            ch1 = eqparser.Node('BINARYOP', [pa.children[0], pa.children[1].children[0]], pa.leaf)
            pa1 = eqparser.Node('BINARYOP', [ch1, pa.children[1].children[1]], opdict2[ch.leaf])
            pa1 = simpTree(pa1)
            heu = 0
            estmHeu(pa1)
            formula1 = 2 + heu
            ch2 = eqparser.Node('BINARYOP', [pa.children[0], pa.children[1].children[1]], pa.leaf)
            pa2 = eqparser.Node('BINARYOP', [ch2, pa.children[1].children[0]], opdict2[ch.leaf])
            pa2 = simpTree(pa2)
            heu = 0
            estmHeu(pa2)
            formula2 = 2 + heu
            return pa1 if formula1 < formula2 else pa2
        if pa.children[1].type in numSet or pa.children[1].type in varSet:
            ch1 = eqparser.Node('BINARYOP', [pa.children[0].children[1], pa.children[1]], opdict2[ch.leaf])
            pa1 = eqparser.Node('BINARYOP', [pa.children[0].children[0], ch1], ch.leaf)
            pa1 = simpTree(pa1)
            heu = 0
            estmHeu(pa1)
            formula1 = 2 + heu
            ch2 = eqparser.Node('BINARYOP', [pa.children[0].children[0], pa.children[1]], pa.leaf)
            pa2 = eqparser.Node('BINARYOP', [ch2, pa.children[0].children[1]], ch.leaf)
            pa2 = simpTree(pa2)
            heu = 0
            estmHeu(pa2)
            formula2 = 2 + heu
            return pa1 if formula1 < formula2 else pa2
    return pa



# After the associativity is applied, this function alter the structure of the tree.

def alterTree(tree, check=None, alter=None):    
    if tree and tree == check:
        return alter
    if tree.children == [ ]:
        return tree
    if tree.type == 'BINARYOP':
        ch0 = alterTree(tree.children[0], check, alter)
        ch1 = alterTree(tree.children[1], check, alter)
        return eqparser.Node('BINARYOP', [ch0, ch1], tree.leaf)
    else:
        ch = alterTree(tree.children, check, alter)
        return eqparser.Node(tree.type, ch, tree.leaf)



# Given a tree, the function execute the associativity rule and alter the tree's
# structure.

def solvTree(tree):
    global index
    for i in range(LOOP_NUM):
        for index in range(1,10):
            fl = findLeaf(tree)
            if fl:
                if len(fl) > 1:
                    fl = [fl[0], fl[1]]
                    check = fl[1]
                    alter = assoTree(fl)
                    tree = alterTree(tree, check, alter)
    return tree
    


# my solution
#s = '3*sqrt(x-1)=2+5'
#s = 'x=((2+5)/3)^2+1'
#s = 'cos(x)= 5'
#s = 'sqrt(a*(sin(x)+b))=cos(c)'
#s = '(2+x)^5=1'
#s = 'x=cos(a+1)*(4/b)+2'
#s = 'x=a*a+1'
#s = '2*x*3=800'
#s = 'x+5=1+a+3+b'
#s = 'x=a*(2+c)'
#s = 'x=1+a-b-(-c)+2*7-(-1)'
#s = 'e^x=9'
#s = 'e^x = z*1'
#s = 'x=(a+1+2)*(sin(b))'
#s = 'x=ln(e)'
#s = 'x=log(10)'

heu = 0
index = 100

# Sample unit test
#s = 'x = (2 + 10) * (2^2)'
#s = 'x = 6 * 2 / (-1 + 4 * 0 + 1)'
#s = '2 * x * 3 * y * 4 * z * 5 * 6 = 800'
#s = '(2 * sqrt(x) * 3) - y = pi'
#s = 'e^x = z * (sin(y)^2 + cos(y)^2)'


while 1:
    try:
        s = raw_input('Eq. > ')
        v = raw_input('Var. > ')
    except EOFError:
        print
        break
    p = eqparser.parse(s)
    fx = findx(p, v)
    if fx[0].children[1] == fx[1]:
        p = switchSide(p)

    newTree = fx[0]
    goalTree(fx)

    newTree = simpTree(newTree.children[1])

    estmHeu(newTree)
    newTree = solvTree(newTree)
    newTree = simpTree(newTree)

    print 'Solution: ', str(newTree)

