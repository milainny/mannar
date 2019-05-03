import numpy as np
import cv2
import queue as qu
import useful as us
import graph as gr
import ocr
import copy
import collections as col
import pandas as pd

def mapping(G,img,label):
    obj = []
    i = 0
    for c in G.nodes():
        x0 = gr.getNodeX0(G,c)
        y0 = gr.getNodeY0(G,c)
        obj.append(('c', (x0,y0),i))
        i = i -1
    for i in range(1,label):
        if(len(np.where(img == i)[0])!=0):
            k,b = us.crop(img,i)
            x,y = k.shape
            minX = np.min(np.where(img == i)[0])
            maxX = np.max(np.where(img == i)[0])
            minY = np.min(np.where(img == i)[1])
            maxY = np.max(np.where(img == i)[1])
            x = (maxX-minX)//2
            y = (maxY-minY)//2
            x = minX+x
            y = minY+y
            obj.append(('n',(x,y),i))
    ob = []
    for i in range(len(obj)):
        q = qu.PriorityQueue()
        xi = obj[i][1][0]
        yi = obj[i][1][1]
        if(obj[i][0] != 'c'):
            for j in range(len(obj)):
                if (i!=j):
                    xj = obj[j][1][0]
                    yj = obj[j][1][1]
                    dist = np.sqrt((xi-xj)**2 +((yi-yj)**2))
                    q.put((dist,obj[j][2]))
        q2 = []
        while(not q.empty()):
            f = q.get()
            q2.append(f)
        ob.append((obj[i][0],(xi,yi),obj[i][2],q2))
    return ob

def discoverArrows(G,img,label,objects,lps,withLps):
    lps =  set(lps)
    numbers = []
    withLps = set(withLps)
    for i in range(1,label):
        if((np.where(img==i))[0].size != 0):
            j,b = us.crop(img,i)
            t = False
            if(b):
                j = np.where(j==i, 0, j)
                j = np.where(j!=0,255,j)
                x,y = j.shape
                j = np.ones_like(img)*255
                j = np.where(img==i,0,j)
                op, img, num = discoverOneArrow(G,j,x,y,img,objects,i,lps,withLps)
                if(op == 1):
                    numbers.append(num)

            else:
                t = True

    av,med = averageComponents(G,numbers,img,label)
    searchOthersComponents(G,objects,numbers,img,label,av,med)
    return img

def discoverOneArrow(G,img,x,y,imgOrg,objects,label,lps,withLps):
    minX = np.min(np.where(img == 0)[0])
    maxX = np.max(np.where(img == 0)[0])
    minY = np.min(np.where(img == 0)[1])
    maxY = np.max(np.where(img == 0)[1])
    pts = []
    #top
    for i in range(minY,maxY+1):
        if(img[minX][i] == 0):
            ptop = (minX,i)
            pts.append(ptop)
            break
    #bottom
    for i in range(minY,maxY+1):
        if(img[maxX][i] == 0):
            pbot = (maxX,i)
            pts.append(pbot)
            break
    #left
    for i in range(minX,maxX+1):
        if(img[i][minY] == 0):
            plef = (i,minY)
            pts.append(plef)
            break
    #right
    for i in range(minX,maxX+1):
        if(img[i][maxY] == 0):
            prig = (i,maxY)
            pts.append(prig)
            break
    size = len(G.nodes())
    vec = [0]*size
    q = qu.PriorityQueue()
    pos = 0
    names = []
    for c in G.nodes():
        names.append(c)
    for c in G.nodes():
        x0 = gr.getNodeX0(G,c)
        y0 = gr.getNodeY0(G,c)
        r  = gr.getNodeRadius(G,c)
        name = c
        if(x>y):
            disttop = np.sqrt((x0-ptop[0])**2 +(y0-ptop[1])**2)
            distbot = np.sqrt((x0-pbot[0])**2 +(y0-pbot[1])**2)
            q.put((disttop,name,pos))
            q.put((distbot,name,pos))

        else:
            distlef = np.sqrt((x0-plef[0])**2 +(y0-plef[1])**2)
            distrig = np.sqrt((x0-prig[0])**2 +(y0-prig[1])**2)
            q.put((distlef,name,pos))
            q.put((distrig,name,pos))

        pos= pos+1

    po = []
    for i in range(2):
        d,n,pos = q.get()
        vec[pos] = vec[pos]+1
        po.append(pos)

    counter = 0
    for v in vec:
        if v == 2:
            break
        if v == 1:
            counter +=1
    if counter == 2:
        obj1 = getObject(objects,po[0]*-1)
        obj2 = getObject(objects,po[1]*-1)

        nobj1 = str(obj1[1][0])+str(obj1[1][1])
        nobj2 = str(obj2[1][0])+str(obj2[1][1])
        if(checkArrow(G,img,x,y, obj1, obj2)):
            dir = arrowDirection(img)
            newI = copy.deepcopy(img)
            newI = cv2.threshold(newI,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
            l = 255
            minX = np.min(np.where(newI == l)[0])
            maxX = np.max(np.where(newI == l)[0])
            minY = np.min(np.where(newI == l)[1])
            maxY = np.max(np.where(newI == l)[1])
            point = (minX,minY)

            text = ''
            num = []
            poi = []
            ims = []
            num.append(label)
            poi.append(point)
            ims.append(newI[minX:maxX,minY:maxY])
            if(dir == 0):
                if(obj1[1][0] > obj2[1][0]):
                    if(G.has_edge(nobj1,nobj2)):

                        num = gr.getEdgeNum(G,nobj1,nobj2)
                        num.append(label)
                        poi = gr.getEdgePoint(G,nobj1,nobj2)
                        poi.append(point)
                        gr.setEdgePoint(G,nobj1,nobj2, poi)
                        ims = gr.getEdgeImg(G,nobj1,nobj2)
                        ims.append(newI[minX:maxX,minY:maxY])
                        gr.setEdgeImg(G,nobj1,nobj2,ims)
                        gr.setEdgeNum(G, nobj1, nobj2, num)
                    else:
                        gr.addEdge(G,nobj1,nobj2,text,num,poi,ims)

                else:
                    if(G.has_edge(nobj2,nobj1)):
                        num = gr.getEdgeNum(G,nobj2,nobj1)
                        num.append(label)
                        poi = gr.getEdgePoint(G,nobj2,nobj1)
                        poi.append(point)
                        gr.setEdgePoint(G,nobj2,nobj1, poi)
                        ims = gr.getEdgeImg(G,nobj2,nobj1)
                        ims.append(newI[minX:maxX,minY:maxY])
                        gr.setEdgeImg(G,nobj2,nobj1,ims)
                        gr.setEdgeNum(G, nobj2, nobj1, num)

                    else:
                        gr.addEdge(G,nobj2, nobj1,text,num,poi,ims)
            elif(dir == 1):
                if(obj1[1][0] > obj2[1][0]):
                    if(G.has_edge(nobj2,nobj1)):
                        num = gr.getEdgeNum(G,nobj2,nobj1)
                        num.append(label)
                        poi = gr.getEdgePoint(G,nobj2,nobj1)
                        poi.append(point)
                        gr.setEdgePoint(G,nobj2,nobj1, poi)
                        ims = gr.getEdgeImg(G,nobj2,nobj1)
                        ims.append(newI[minX:maxX,minY:maxY])
                        gr.setEdgeImg(G,nobj2,nobj1,ims)
                        gr.setEdgeNum(G, nobj2, nobj1, num)

                    else:
                        gr.addEdge(G,nobj2, nobj1,text,num,poi,ims)

                else:
                    if(G.has_edge(nobj1,nobj2)):
                        num = gr.getEdgeNum(G,nobj1,nobj2)
                        num.append(label)
                        poi = gr.getEdgePoint(G,nobj1,nobj2)
                        poi.append(point)
                        gr.setEdgePoint(G,nobj1,nobj2, poi)
                        ims = gr.getEdgeImg(G,nobj1,nobj2)
                        ims.append(newI[minX:maxX,minY:maxY])
                        gr.setEdgeImg(G,nobj1,nobj2,ims)
                        gr.setEdgeNum(G, nobj1, nobj2, num)
                    else:
                        gr.addEdge(G,nobj1,nobj2,text,num,poi,ims)

            elif(dir == 2):
                if(obj1[1][1] > obj2[1][1]):
                    if(G.has_edge(nobj1,nobj2)):
                        num = gr.getEdgeNum(G,nobj1,nobj2)
                        num.append(label)
                        poi = gr.getEdgePoint(G,nobj1,nobj2)
                        poi.append(point)
                        gr.setEdgePoint(G,nobj1,nobj2, poi)
                        ims = gr.getEdgeImg(G,nobj1,nobj2)
                        ims.append(newI[minX:maxX,minY:maxY])
                        gr.setEdgeImg(G,nobj1,nobj2,ims)
                        gr.setEdgeNum(G, nobj1, nobj2, num)
                    else:
                        gr.addEdge(G,nobj1,nobj2,text,num,poi,ims)
                else:
                    if(G.has_edge(nobj2,nobj1)):
                        num = gr.getEdgeNum(G,nobj2,nobj1)
                        num.append(label)
                        poi = gr.getEdgePoint(G,nobj2,nobj1)
                        poi.append(point)
                        gr.setEdgePoint(G,nobj2,nobj1, poi)
                        ims = gr.getEdgeImg(G,nobj2,nobj1)
                        ims.append(newI[minX:maxX,minY:maxY])
                        gr.setEdgeImg(G,nobj2,nobj1,ims)
                        gr.setEdgeNum(G, nobj2, nobj1, num)
                    else:
                        gr.addEdge(G,nobj2, nobj1,text,num,poi,ims)

            elif(dir == 3):
                if(obj1[1][1] > obj2[1][1]):
                    if(G.has_edge(nobj2,nobj1)):
                        num = gr.getEdgeNum(G,nobj2,nobj1)
                        num.append(label)
                        poi = gr.getEdgePoint(G,nobj2,nobj1)
                        poi.append(point)
                        gr.setEdgePoint(G,nobj2,nobj1, poi)
                        ims = gr.getEdgeImg(G,nobj2,nobj1)
                        ims.append(newI[minX:maxX,minY:maxY])
                        gr.setEdgeImg(G,nobj2,nobj1,ims)
                        gr.setEdgeNum(G, nobj2, nobj1, num)
                    else:
                        gr.addEdge(G,nobj2,nobj1,text,num,poi,ims)
                else:
                    if(G.has_edge(nobj1,nobj2)):
                        num = gr.getEdgeNum(G,nobj1,nobj2)
                        num.append(label)
                        poi = gr.getEdgePoint(G,nobj1,nobj2)
                        poi.append(point)
                        gr.setEdgePoint(G,nobj1,nobj2, poi)
                        ims = gr.getEdgeImg(G,nobj1,nobj2)
                        ims.append(newI[minX:maxX,minY:maxY])
                        gr.setEdgeImg(G,nobj1,nobj2,ims)
                        gr.setEdgeNum(G, nobj1, nobj2, num)
                    else:
                        gr.addEdge(G,nobj1,nobj2,text,num,poi,ims)

            return 1, imgOrg,label
    else:
        pass


    return 2, imgOrg, 0

def checkArrow(G,img, x,y,obj1, obj2):
    nobj1 = str(obj1[1][0])+str(obj1[1][1])
    nobj2 = str(obj2[1][0])+str(obj2[1][1])
    r1 = gr.getNodeRadius(G,nobj1)
    r2 = gr.getNodeRadius(G,nobj2)
    #tamanho = x*y
    tam = len(np.where(img==0)[0])
    dist =  np.sqrt((obj1[1][0]-obj2[1][0])**2 +(obj1[1][1]-obj2[1][1])**2) - r1 - r2
    if(tam>=int(dist)):
        j,b = us.crop(img,0)
        if (x >= y):
            cont1 = len(np.where(j[0,:]==0)[0])
            cont2 = len(np.where(j[x-1,:]==0)[0])
        else:
            cont1 = len(np.where(j[:,0]==0)[0])
            cont2 = len(np.where(j[:,y-1]==0)[0])
        if((x< 30 and x*2 < y) or (y < 30 and y*2 < x)):
            return True
        else:
            if(x>dist or y >dist):
                return True
            else:
                white = (x*y) - tam
                if (white > tam and (white/tam)>5):
                    return True
    return False

def arrowDirection(img):
    j,b = us.crop(img,0)
    x,y = j.shape
    arq = open('x.txt', 'w')
    arq.write(str(j))
    arq.close()
    if (x>=y):
        nx = x//4
        if(nx > 5):
            nx = 5
        count1 = len(np.where(j[0:nx,:]==0)[0])
        count2 = len(np.where(j[x-nx:x,:]==0)[0])
        if(count1>count2):
            return 0
        else:
            return 1
    else:
        ny = y //4
        count1 = len(np.where(j[:,0:ny]==0)[0])
        count2 = len(np.where(j[:,y-ny:y]==0)[0])
        if(count1>count2):
            return 2
        else:
            return 3

def getObject(ob,num):
    for o in ob:
        if(o[2] == num):
            return o
    return 0

def averageComponents(G,numbers,img,label):
    counter = 0
    med = []
    sum = 0
    xx,yy = img.shape
    for i in range(1,label):
        if((np.where(img==i))[0].size != 0):
            if i not in numbers:
                j,b = us.crop(img,i)
                j = np.where(j!=i,255,j)
                x,y = j.shape
                a = x*y
                if(xx*yy != a):
                    med.append(a)
                    sum +=a
                    counter +=1
    med = pd.Series(med)
    return sum/counter,med.median()

def searchOthersComponents(G,objects,numbers,img,label,av,med):
    t = img.shape[0]*img.shape[1]
    img1 = copy.deepcopy(img)
    arrow = []
    text = []
    initial = []
    for i in range(1,label):
        if((np.where(img==i))[0].size != 0):
            if i not in numbers:
                j,b = us.crop(img,i)
                j = np.where(j!=i,255,j)
                classifierArrowOrText(j,i,av,med,t,numbers,arrow,text,initial)

    if(len(arrow) > 0):
        addArrows(G, arrow, img1)
    if(len(initial) >0):
        addInitial(G,initial,img1)
    img1, numbers,label,index = completImage(G,img1,numbers,label)

    for i in index:
        objects.append(('c',(i[1],i[2]),i[0],[]))
    list, objs,nimg,label2 = searchLabelsArrows(G,objects,numbers,img1,initial)
    numbers2 = []
    list2 =[]
    for l in list:
        list2.append(l[1])
    for o in objs:
        if(o[2] > 0 and o[2] not in list2):
            numbers2.append(o[2])
            newI = np.ones_like(nimg)*255
            newI = np.where(nimg==o[2],0,newI)

    saveText(G,list,list2,objs,nimg,numbers2,index)

def classifierArrowOrText(img,label,av,med,t,numbers,arrow,text,initial):
    obj = len(np.where(img == label)[0])
    x,y = img.shape
    a = x*y
    if(av<=med):
        menor = av
        maior = med
    else:
        menor = med
        maior = av

    maior2 = maior*2
    menor2 = menor*2

    if(obj > 0 and a != t):
        obj1 = (x*y)-obj
        if(x>y):
            ecc = x/y
            minnor = y
        else:
            ecc = y/x
            minnor = x
        if (a >= maior2):
            if(obj/obj1 < 0.3):
                ims,b = us.crop(img,label)
                x = checkInitial(ims,label)
                if(x == 1):
                    numbers.append(label)
                    arrow.append(label)
                else:
                    initial.append(label)
            else:
                initial.append(label)
        elif (a >= menor):
            if(obj1 > 0):
                if(ecc >= 2.5 and obj/obj1 < 1.1):
                    initial.append(label)
                elif(obj/obj1 < 0.3):
                    numbers.append(label)
                    arrow.append(label)
                else:
                    text.append(label)
        elif(a < menor):

            if(ecc > 3 and minnor > 10):
                initial.append(label)

            text.append(label)

    return numbers, arrow, text,initial

def addArrows(G, arrow, img):
    for a in arrow:
        cir = getClosestCircle(G, a, img)

        newI = np.ones_like(img)*255
        newI = np.where(img==a,0,newI)
        newI = cv2.threshold(newI,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
        l = 255
        minX = np.min(np.where(newI == l)[0])
        maxX = np.max(np.where(newI == l)[0])
        minY = np.min(np.where(newI == l)[1])
        maxY = np.max(np.where(newI == l)[1])
        point = (minX,minY)
        cir2 = ((maxX-minX)//2,(maxY-minY)//2,0)
        num = []
        poi = []
        ims = []
        num.append(a)
        poi.append(point)
        ims.append(newI[minX:maxX,minY:maxY])
        if(G.has_edge(cir,cir)):
            num = gr.getEdgeNum(G,cir,cir)
            num.append(a)
            poi = gr.getEdgePoint(G,cir,cir)
            poi.append(point)
            gr.setEdgePoint(G,cir,cir, poi)
            ims = gr.getEdgeImg(G,cir,cir)
            ims.append(newI[minX:maxX,minY:maxY])
            gr.setEdgeImg(G,cir,cir,ims)
            gr.setEdgeNum(G, cir, cir, num)
        else:
            gr.addEdge(G,cir,cir,'',num,poi,ims)
            gr.addNodeLoop(G,cir,cir2)

def addInitial(G,initial,img):
    for i in initial:
        cir = getClosestCircle(G,i,img)
        gr.setInitialState(G,cir)

def getClosestCircle(G,e,img):
    objs = []
    for n in G.nodes():
        x0 = gr.getNodeX0(G,n)
        y0 = gr.getNodeY0(G,n)
        objs.append(('c',(x0,y0),0))


    minX = np.min(np.where(img == e)[0])
    maxX = np.max(np.where(img == e)[0])
    minY = np.min(np.where(img == e)[1])
    maxY = np.max(np.where(img == e)[1])
    x = (maxX-minX)//2
    y = (maxY-minY)//2
    x = minX+x
    y = minY+y
    q = qu.PriorityQueue()
    for i in range(len(objs)):
        xi = objs[i][1][0]
        yi = objs[i][1][1]
        name = str(objs[i][1][0]) + str(objs[i][1][1])
        xj = x
        yj = y
        dist = np.sqrt((xi-xj)**2 +((yi-yj)**2))
        q.put((dist,name))

    cir = q.get()

    return cir[1]

def completImage(G,img1,numbers,label):
    index = []
    for e in G.edges():
        poi = gr.getEdgePoint(G,e[0],e[1])
        for i in range(len(poi)):
            l = gr.getEdgeNum(G,e[0],e[1])[i]
            if (l == -1):
                point = gr.getEdgePoint(G,e[0],e[1])[i]
                j = gr.getEdgeImg(G,e[0],e[1])[i]
                x,y = j.shape
                j = np.where(j == 255, label, j)
                img1[point[0]:point[0]+x,point[1]:point[1]+y] = np.where(j == label,j,img1[point[0]:point[0]+x,point[1]:point[1]+y])
                numbers.append(label)
                index.append((label,(point[0]+x)//2,(point[1]+y)//2,e[0],e[1]))
                label +=1

    return img1, numbers, label, index

def searchLabelsArrows(G,objects,numbers,imgOrg,initial):

    img = copy.deepcopy(imgOrg)
    objs = copy.deepcopy(objects)
    boolean = False
    contF = 0
    fat = 0
    numOrg = []
    for n in numbers:
        numOrg.append(n)

    first = True
    while True:
        imgRes = np.ones_like(img)*255
        counter = 1
        list = []
        check = []
        num = []
        for o in objs:
            obj1 = o[2]
            if(o[0]!='c' and not obj1 in numbers):
                obj2 = o[3][0][1]

                if((obj2 in initial or obj1 in initial) and first):
                    pass
                elif(obj2 <= 0 or obj2 in numbers):
                        list.append(obj1)
                        imgRes = np.where(img==obj1,counter,imgRes)

                        counter +=1
                else:
                    obj3 = getFistList(objs,obj2)
                    if(obj3 == obj1):
                        if(not obj2 in check and not obj1 in check):
                            imgRes = np.where(img==obj1,counter,imgRes)
                            imgRes = np.where(img==obj2,counter,imgRes)
                            check.append(obj1)
                            check.append(obj2)
                            counter +=1
                            boolean = True
                    else:
                        imgRes = np.where(img==obj1,counter,imgRes)

                        counter +=1
            else:
                 if(obj1 in numbers):
                     imgRes = np.where(img==obj1,counter,imgRes)

                     num.append(counter)
                     counter +=1
        first = False

        numbers = copy.deepcopy(num)
        objs = mapping(G,imgRes,counter)
        img = copy.deepcopy(imgRes)

        if(not boolean):
            list = []
            numOrg.sort()
            for i in range(len(numOrg)):
                list.append((numOrg[i],numbers[i]))
            break
        else:
            boolean = False
    return list, objs, img,counter

def getFistList(objects,obj):
    for o in objects:
        if (o[2] == obj):
            return o[3][0][1]
    return obj

def saveText(G,list, list2,objs,nimg,numbers,index):
    x,y = nimg.shape

    for n in numbers:
        j,b = us.crop(nimg,n)

        newI = np.ones_like(nimg)*255
        newI = np.where(nimg==n,0,newI)

        #problama dos ruidos

        minX = np.min(np.where(nimg == n)[0])
        maxX = np.max(np.where(nimg == n)[0])
        minY = np.min(np.where(nimg == n)[1])
        maxY = np.max(np.where(nimg == n)[1])
        medX = minX + (maxX - minX) //2
        medY = minY + (maxY - minY) //2

        if(len(np.where(j == n)[0]) > 5): #verifica ruidos
            cont = 0
            while True:
                if(maxX+cont < x):
                    if(nimg[maxX+cont][medY] != 255 and nimg[maxX+cont][medY] != n):
                        if(nimg[maxX+cont][medY] in list2):
                            text = ocr.labelToText(newI)
                            nn = searchOriginal(list,nimg[maxX+cont][medY])
                            e0, e1 = gr.getEdgeByNum(G,nn)
                            if(e0 == -1):
                                for i in index:
                                    if(i[0] == nn):
                                        e0 = i[3]
                                        e1 = i[4]
                            t = gr.getEdgeLabel(G,e0,e1)
                            t = t +","+text
                            gr.setEdgeLabel(G,e0,e1,t)
                            break
                if(maxY + cont < y):
                    if(nimg[medX][maxY+cont] != 255 and nimg[medX][maxY+cont] != n):
                        if(nimg[medX][maxY+cont] in list2):

                            text = ocr.labelToText(newI)
                            nn = searchOriginal(list,nimg[medX][maxY+cont])
                            e0, e1 = gr.getEdgeByNum(G,nn)
                            if(e0 == -1):
                                for i in index:
                                    if(i[0] == nn):
                                        e0 = i[3]
                                        e1 = i[4]
                            t = gr.getEdgeLabel(G,e0,e1)
                            t = t +","+text
                            gr.setEdgeLabel(G,e0,e1,t)
                            break
                if(minX - cont > 0):
                    if(nimg[minX-cont][medY] != 255 and nimg[minX-cont][medY] != n):
                        if(nimg[minX-cont][medY] in list2):
                            text = ocr.labelToText(newI)
                            nn = searchOriginal(list,nimg[minX-cont][medY])
                            e0, e1 = gr.getEdgeByNum(G,nn)
                            if(e0 == -1):
                                for i in index:
                                    if(i[0] == nn):
                                        e0 = i[3]
                                        e1 = i[4]
                            t = gr.getEdgeLabel(G,e0,e1)
                            t = t +","+text
                            gr.setEdgeLabel(G,e0,e1,t)
                            break
                if(minY - cont > 0):
                    if(nimg[medX][minY-cont] != 255 and nimg[medX][minY-cont] != n):
                        if(nimg[medX][minY-cont] in list2):
                            text = ocr.labelToText(newI)
                            nn = searchOriginal(list,nimg[medX][minY-cont])
                            e0, e1 = gr.getEdgeByNum(G,nn)
                            if(e0 == -1):
                                for i in index:
                                    if(i[0] == nn):
                                        e0 = i[3]
                                        e1 = i[4]
                            t = gr.getEdgeLabel(G,e0,e1)
                            t = t +","+text
                            gr.setEdgeLabel(G,e0,e1,t)
                            break
                if(minX-cont > 0 and minY - cont > 0):
                    if(nimg[minX-cont][minY-cont] != 255 and nimg[minX-cont][minY-cont] != n):
                        if(nimg[minX-cont][minY-cont] in list2):
                            text = ocr.labelToText(newI)
                            nn = searchOriginal(list,nimg[minX-cont][minY-cont])
                            e0, e1 = gr.getEdgeByNum(G,nn)
                            if(e0 == -1):
                                for i in index:
                                    if(i[0] == nn):
                                        e0 = i[3]
                                        e1 = i[4]
                            t = gr.getEdgeLabel(G,e0,e1)
                            t = t +","+text
                            gr.setEdgeLabel(G,e0,e1,t)
                            break
                if(maxX+cont < x-1 and minY - cont > 0):
                    if(nimg[maxX+cont][minY-cont] != 255 and nimg[maxX+cont][minY-cont] != n):
                        if(nimg[maxX+cont][minY-cont] in list2):
                            text = ocr.labelToText(newI)
                            nn = searchOriginal(list,nimg[maxX+cont][minY-cont])
                            e0, e1 = gr.getEdgeByNum(G,nn)
                            if(e0 == -1):
                                for i in index:
                                    if(i[0] == nn):
                                        e0 = i[3]
                                        e1 = i[4]
                            t = gr.getEdgeLabel(G,e0,e1)
                            t = t +","+text
                            gr.setEdgeLabel(G,e0,e1,t)
                            break
                if(minX - cont > 0 and maxY + cont < y-1):
                    if(nimg[minX-cont][maxY+cont] != 255 and nimg[minX-cont][maxY+cont] != n):
                        if(nimg[minX-cont][maxY+cont] in list2):
                            text = ocr.labelToText(newI)
                            nn = searchOriginal(list,nimg[minX-cont][maxY+cont])
                            e0, e1 = gr.getEdgeByNum(G,nn)
                            if(e0 == -1):
                                for i in index:
                                    if(i[0] == nn):
                                        e0 = i[3]
                                        e1 = i[4]
                            t = gr.getEdgeLabel(G,e0,e1)
                            t = t +","+text
                            gr.setEdgeLabel(G,e0,e1,t)
                            break
                if(maxX + cont < x - 1 and maxY + cont < y-1):
                    if(nimg[maxX+cont][maxY+cont] != 255 and nimg[maxX+cont][maxY+cont] != n):
                        if(nimg[maxX+cont][maxY+cont] in list2):
                            text = ocr.labelToText(newI)
                            nn = searchOriginal(list,nimg[maxX+cont][maxY+cont])
                            e0, e1 = gr.getEdgeByNum(G,nn)
                            if(e0 == -1):
                                for i in index:
                                    if(i[0] == nn):
                                        e0 = i[3]
                                        e1 = i[4]
                            t = gr.getEdgeLabel(G,e0,e1)
                            t = t +","+text
                            gr.setEdgeLabel(G,e0,e1,t)
                            break
                if(minY - cont < 0 and minX - cont < 0 and maxX + cont > x-1 and maxY + cont > y-1):
                    break
                cont +=1


def searchOriginal(list,n):
    for l in list:
        if l[1] == n:
            return l[0]


def checkInitial(img,label):
    x,y = img.shape
    i = 0
    if (x >= y):
        passo = x // 4
        i = passo
        cont1 = len(np.where(img[:i,:] == label)[0])
        cont2 = len(np.where(img[i:i+passo,:] == label)[0])
        i = i + passo
        cont3 = len(np.where(img[i:i+passo,:] == label)[0])
        i = i + passo
        cont4 = len(np.where(img[i:i+passo,:] == label)[0])
    else:
        passo = y // 4
        i = passo
        cont1 = len(np.where(img[:, :i] == label)[0])
        cont2 = len(np.where(img[:, i:i+passo] == label)[0])
        i = i + passo
        cont3 = len(np.where(img[:, i:i+passo] == label)[0])
        i = i + passo
        cont4 = len(np.where(img[:, i:i+passo] == label)[0])

    if(cont1<=cont4):
        res = abs(cont1 - cont2)
        res2 = abs(cont2 - cont3)
        if(res <=5 and res2 <=5):
            return 0
        else:
            return 1
    else:
        res = abs(cont4 - cont3)
        res2 = abs(cont3 - cont2)
        if(res <=5 and res2 <=5):
            return 0
        else:
            return 1
