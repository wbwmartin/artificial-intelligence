from graphviz import Digraph



# A tree class includes the attribute: a list of children pointers, a boolean
# to check if it is selecting max or min, a utility value.

class Tree:
    def __init__(self, val, children=None, isMax=None, util=0):
        self.val = val
        self.children = children
        self.util = util



# Use dynammic programming to build the minimax tree.

def buildTree(n):
    ls = []
    ls.append(Tree(1))
    ls.append(Tree(2, [ls[0]]))
    ls.append(Tree(3, [ls[0], ls[1]]))
    if n > 3:
        for i in range(3, n):
            ls.append(Tree(i+1, [ls[i-3], ls[i-2], ls[i-1]]))
    return ls[n-1]



# Set the utility at the leaf. If it is max, utility = -1, else, utility = 1.

def setUtil(root):
    if not root.children:
        temp = -1 if root.isMax else 1
        return Tree(1, None, root.isMax, temp)
    else:
        ls = []
        for x in root.children:
            x.isMax = not root.isMax
            ls.append(setUtil(x))
        return Tree(root.val, ls, root.isMax, root.util)



# Minimax Algorithm to help the player make the optimized decision.

def miniMax(root):
    if not root.children:
        return "You lose!"
    ls = []
    rst = 0
    val = -10
    for i in range(len(root.children)):
        ls.append(minValue(root.children[i]))
        if ls[i] > val:
            val = ls[i]
            rst = i
    if val > -1:
        return "Choose " + str(len(root.children) - rst)
    else:
        return "You have no choice. Just choose 1."
        


# It returns an optimized maximum value by searching through the next level.
# When it reaches the leaf, returns the utility.

def maxValue(node):
    if not node.children:
        return node.util
    util = -10
    for x in node.children:
        util = max(util, minValue(x))
    return util



# It returns an optimized minimum value by searching through the next level.
# When it reaches the leaf, returns the utility.

def minValue(node):
    if not node.children:
        return node.util
    util = 10
    for x in node.children:
        util = min(util, maxValue(x))
    return util
        


# To visualize the tree using package graphviz.

def vizTree(root):
    global dot, index
    if not root.children:
        if index == 0:
            index += 1
            dot.node(str(index), label='1') 
    else:
        dot.node(str(index), label=str(root.val))
        pid = index
        for x in root.children:
            index += 1
            dot.node(str(index), label=str(x.val))
            dot.edge(str(pid), str(index))
            vizTree(x)
    return



# Unit test.

n = input("Enter an initial number n: ")
root = buildTree(n)
root.isMax = True
index = 0
dot = Digraph()
root = setUtil(root)
vizTree(root)
dot.render('tree/mm'+str(n)+'.gv')
#print (dot.source)
#print index+1

