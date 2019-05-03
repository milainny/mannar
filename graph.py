import numpy as np
import cv2
import useful as us
import queue as qu
import networkx as nx
#import transactions as tr
import graph as gr
import ocr
import matplotlib.pyplot as plt
import collections as col

def getNodeLabel(G,name):
    return G.node[name]['label']

def getNodeX0(G,name):
    return G.node[name]['x0']

def getNodeY0(G,name):
    return G.node[name]['y0']

def getNodeRadius(G,name):
    return G.node[name]['radius']

def getNodeLoop(G,name):
    return G.node[name]['loop']

def getNodePoint(G,name):
    return G.node[name]['point']

def getNodeImg(G,name):
    return G.node[name]['img']

def getEdgePoint(G,x,y):
    return G[x][y]['point']

def getEdgeImg(G,x,y):
    return G[x][y]['img']

def getNodeBegin(G,name):
    return G.node[name]['begin']

def getNodeAccept(G,name):
    return G.node[name]['accept']

def getEdgeLabel(G,x,y):
    return G[x][y]['label']

def getEdgeNum(G,x,y):
    return G[x][y]['num']

def getEdgeByNum(G, nn):
    for e in G.edges():
        n = getEdgeNum(G,e[0],e[1])
        for i in range(len(n)):
            if (n[i] == nn):
                return e[0],e[1]
    return -1,-1

def addNodes(G,accept,circles,imgOrg):
    accept = set(accept)
#    names = []
    for i in range(len(circles)):
        name = str(circles[i][1][0])+str(circles[i][1][1])
        x0 = circles[i][1][0]
        y0 = circles[i][1][1]
        radius = circles[i][1][2]
        loop = circles [i][2]
        acc = circles[i][3]
        text = circles[i][4]
        point = circles[i][5]
        img = circles[i][6]
        if (not loop):
            G.add_node(name, label=text, begin=False, accept=acc, loop=[], x0=x0, y0=y0, radius=radius, point = point, img = img) #, error=circles[i][0]
    return G

def addEdge(G,e1,e2,label,num=[],point=[],img=[]):
    G.add_edge(e1,e2,label=label,num=num,point=point,img=img)

def addNodeLoop(G,name,loop):
    G.node[name]['loop'].append(loop)

def setArrowLabel(G,num,text):
    for e in G.edges():
        x,y = e
        if(G[x][y]['num'] == num):
            G[x][y]['label'] = text

def setEdgeLabel(G,x,y,text):
    G[x][y]['label'] = text

def setEdgeNum(G,x,y,num):
    G[x][y]['num'] = num

def setEdgePoint(G,x,y,poi):
    G[x][y]['point'] = poi

def setEdgeImg(G,x,y,img):
    G[x][y]['img'] = img

def setLoopLabel(G,cir,text):
    for e in G.edges():
        x,y = e
        name = str(x) + str(y)
        if(name == cir):
            G[x][y]['label'] = text

def setLoopLabel2(G,cir,text):
    for e in G.edges():
        x,y = e
        name = str(x) + str(y)
        if(name == cir+cir):
            G[x][y]['label'] = text


def setInitialState(G,name):
    G.node[name]['begin'] = True

def printGraph(G):
    print(G.nodes())
    for e in G.edges():
        x,y = e
        print(e)
        print(G[x][y]['label'])
        print(len(G[x][y]['point']))
    alfa = ''
    dic = col.defaultdict(list)
    for e in G.edges():
        x,y = e
        #print(e,G[x][y]['label'])
        alfa +=','+G[x][y]['label']
        text = G[x][y]['label']
        text = text.split(',')
        for t in text:
            n = str(x)+'-'+t.strip(" ")
            dic[n].append(str(y))
    #print(alfa)
    alfa = alfa.split(',')
    al = []
    for a in alfa:
        a = a.strip(" ")
        if(a != " " and a != "" and not a in al):
            al.append(a)
    al.sort()
    #print(al)
    prin = "|"
    print(prin.rjust(15),end='')
    for a in al:
        prin = a+"|"
        print(prin.rjust(5),end='')
    print()
    for n in G.nodes():
        desc = ''
        if(G.node[n]['begin']):
            desc = 'ie '
        if(G.node[n]['accept']):
            #print(G.node[n]['accept'])
            desc = desc + 'ae '
        prin = desc+' '+G.node[n]['label']+' '+n+' |'
        print(prin.rjust(15),end='')
        edg = []
        for e in G.edges():
            x,y = e
            #print(e,x,n,y)
            if(n == x and not x in edg):
                #print('entrou',e)
                #print('aa',al)
                edg.append(x)
                for a in al:
                    rdic = dic[str(x)+'-'+a]
                    r = ''
                    #print('rd',rdic)
                    for d in rdic:
                    #    print('d,',d)
                        r += G.node[d]['label']+','
                    r = r[0:len(r)-1]
                    prin = r + "|"
                    print(prin.rjust(5),end='')
                print()
        print()

def printTest(G,accept):
    print('Estados',len(G.nodes))
    print(G.nodes())

    print('Finais')
    print(accept)

    print('Iniciais')
    for n in G.nodes():
        if(G.node[n]['begin']):
            print(n)

    print('Transações')
    print(G.edges())
