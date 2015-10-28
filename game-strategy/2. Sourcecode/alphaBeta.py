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



# Alpha-Beta Algorithm to help the player make the optimized decision. It
# eliminates the useless search so as to reduce the time and space complexity.

def alphaBeta(root):
    global dot, index
    if not root.children:
        info = "You lose!"
        index += 1
        dot.node(str(index), label='1')
        return [info, 0]
    pos = maxValue(root, -1, 1)[1]
    if pos == -1:
        info = "You have no choice. Just choose 1."
        return [info, len(root.children) - 1]
    else:
        rst = len(root.children) - pos
        info = "Choose " + str(rst)
        return [info, pos]

    

# It returns an optimized maximum value by searching through the next level.
# When it reaches the leaf, returns the utility.

def maxValue(node, alpha, beta):
    global dot, index
    if index == 0:
        index += 1
        dot.node(str(index), label=str(node.val), comment='xxx')        
    if not node.children:
        return [node.util, 0]
    util = -10
    pid = index
    for i in range(len(node.children)):
        index += 1
        dot.node(str(index), label=str(node.children[i].val))
        dot.edge(str(pid), str(index))
        util = max(util, minValue(node.children[i], alpha, beta)[0])
        if util >= beta:
            return [util, i]
        alpha = max(alpha, util)
    return [util, -1]



# It returns an optimized minimum value by searching through the next level.
# When it reaches the leaf, returns the utility.

def minValue(node, alpha, beta):
    global dot, index
    if not node.children:
        return [node.util, 0]
    util = 10
    pid = index
    for i in range(len(node.children)):
        index += 1
        dot.node(str(index), label=str(node.children[i].val))
        dot.edge(str(pid), str(index))
        util = min(util, maxValue(node.children[i], alpha, beta)[0])               
        
        if util <= alpha:
            return [util, i]
        beta = min(beta, util)
    return [util, -1]



# Unit test.

n = input("Enter an initial number n: ")
index = 0
root = buildTree(n)
root.isMax = True
dot = Digraph()
root = setUtil(root)
alphaBeta(root)
#dot.render('tree/ab'+str(n)+'.gv')
print index
