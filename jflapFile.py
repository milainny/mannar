from xml.dom.minidom import Document
import urllib
import graph as gr

def createJFlap(G):
    doc = Document()
    base = doc.createElement('structure')

    output = open("automata.jff", "w+")
    doc.appendChild(base)

    type = doc.createElement('type')
    type_cont = doc.createTextNode('fa')
    type.appendChild(type_cont)
    base.appendChild(type)

    automaton = doc.createElement('automaton')

    list = []
    counter = 0
    for g in G.nodes:
        xx,yy = gr.getNodePoint(G,g)
        lab = gr.getNodeLabel(G,g)

        state = doc.createElement('state')
        state.setAttribute('id', str(counter))
        state.setAttribute('name', lab)

        x = doc.createElement('x')
        x_cont = doc.createTextNode(str(yy))
        x.appendChild(x_cont)
        state.appendChild(x)

        y = doc.createElement('y')
        y_cont = doc.createTextNode(str(xx))
        y.appendChild(y_cont)
        state.appendChild(y)

        accept = gr.getNodeAccept(G,g)
        begin = gr.getNodeBegin(G,g)

        if(begin):
            initial = doc.createElement('initial')
            state.appendChild(initial)
        if(accept):
            final = doc.createElement('final')
            state.appendChild(final)

        automaton.appendChild(state)        
        list.append((g,counter))
        counter +=1

    dic = dict(list)
    for e in G.edges:
        xx,yy = e
        p = gr.getEdgePoint(G,xx,yy)
        label = gr.getEdgeLabel(G,xx,yy)

        transition = doc.createElement('transition')

        fro = doc.createElement('from')
        from_cont = doc.createTextNode(str(dic[xx]))
        fro.appendChild(from_cont)
        transition.appendChild(fro)

        to = doc.createElement('to')
        to_cont = doc.createTextNode(str(dic[yy]))
        to.appendChild(to_cont)
        transition.appendChild(to)

        read = doc.createElement('read')
        read_cont = doc.createTextNode(str(label[1:]))
        read.appendChild(read_cont)
        transition.appendChild(read)

        automaton.appendChild(transition)

    base.appendChild(automaton)
    # Escrevendo o arquivo exemplo.xml
    doc.writexml(output," "," ", "\n", "UTF-8")

    #Fechando o arquivo
    output.close()
