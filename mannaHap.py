import json as js
import graph as gr

def createJson(G,org):
    objects = createListObj(G)
    x,y = org.shape
    data = {
    "image":{
        "rows": x,
        "cols": y,
        "objects": objects
    }
    }
    with open("automata.json", "w") as write_file:
        js.dump(data, write_file)

def createListObj(G):
    #objs = "["
    objs = []
    counter = 1
    desc = ""
    for g in G.nodes:
        oneobj = {}
        oneobj["objectID"] = counter
        x,y = gr.getNodePoint(G,g)
        point = []
        point.append(int(x))
        point.append(int(y))
        img = gr.getNodeImg(G,g)
        oneobj["boxCoord"] = point
        oneobj["pixMatrix"] = img.tolist()
        accept = gr.getNodeAccept(G,g)
        begin = gr.getNodeBegin(G,g)
        label = gr.getNodeLabel(G,g)
        if(accept and begin):
            desc = 'Initial and accept state '+label
        elif(begin):
            desc = 'Initial state '+label
        elif(accept):
            desc = 'Accept state '+ label
        else:
            desc = 'State '+label
        oneobj["descObj"] = desc
        objs.append(oneobj)
        counter +=1

    for e in G.edges:
        xx,yy = e
        p = gr.getEdgePoint(G,xx,yy)
        for i in range(0,len(p)):
            oneobj = {}
            oneobj["objectID"] = counter
            x, y = p[i]
            point = []
            point.append(int(x))
            point.append(int(y))
            img = gr.getEdgeImg(G,xx,yy)
            oneobj["boxCoord"] = point
            oneobj["pixMatrix"] = img[i].tolist()
            xxLabel = gr.getNodeLabel(G,xx)
            yyLabel = gr.getNodeLabel(G,yy)
            label = gr.getEdgeLabel(G,xx,yy)
            if(len(label) <= 1):
                desc = "Transition from state "+ str(xxLabel) +" to state "+ str(yyLabel) +" with the symbol "+str(label[1:])
            else:
                desc = "Transition from state "+ str(xxLabel) +" to state "+ str(yyLabel) +" with the symbols "+str(label[1:])
                oneobj["descObj"] = desc
                objs.append(oneobj)
            counter +=1

    return objs
