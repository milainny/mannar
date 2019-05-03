import csv
import graph as gr
import collections as col

def createCsv(G):
    with open('automata.csv', mode='w') as csv_file:
        alfa = ''
        dic = col.defaultdict(list)
        for e in G.edges():
            x,y = e
            alfa +=','+G[x][y]['label']
            text = G[x][y]['label']
            text = text.split(',')
            for t in text:
                n = str(x)+'-'+t.strip(" ")
                dic[n].append(str(y))
        alfa = alfa.split(',')
        al = []
        for a in alfa:
            a = a.strip(" ")
            if(a != " " and a != "" and not a in al):
                al.append(a)
        al.sort()
        fieldnames = []
        fieldnames.append(" ")
        for a in al:
            fieldnames.append(a)
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for n in G.nodes():
            li = []
            desc = ''
            if(G.node[n]['begin']):
                desc = 'ie '
            if(G.node[n]['accept']):
                desc = desc + 'ae '
            prin = desc+' '+G.node[n]['label']+' '+n
            li.append((" ", prin))
            edg = []
            for e in G.edges():
                x,y = e
                if(n == x and not x in edg):
                    edg.append(x)
                    for a in al:
                        rdic = dic[str(x)+'-'+a]
                        r = ''
                        for d in rdic:
                            r += G.node[d]['label']+','
                        r = r[0:len(r)-1]
                        prin = r
                        li.append((a,prin))
                    dicio = dict(li)
                    writer.writerow(dicio)
                else:
                    if (not x in edg):
                        edg.append(x)
                        for a in al:
                            li.append((a,""))
                        dicio = dict(li)
                        writer.writerow(dicio)
