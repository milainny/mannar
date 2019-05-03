import cv2
import queue as qu
import numpy as np

def resizeImg(img):
    if((img.shape[0] > 500 and img.shape[0] < 800) or (img.shape[1] > 500 and img.shape[1] < 800)):
        img = cv2.resize(img,(0,0),fx=0.8, fy=0.8)

    if((img.shape[0] >= 800 and img.shape[0] < 1000) or (img.shape[1] >= 800 and img.shape[1] < 1000)):
        img = cv2.resize(img,(0,0),fx=0.5, fy=0.5)

    if((img.shape[0] >= 1000) or (img.shape[1] >= 1000)):
        img = cv2.resize(img,(0,0),fx=0.4, fy=0.4)
    return img

def showAllcircles(r):
    circles = qu.PriorityQueue()
    i = 0
    k = len(r)
    while (i<k):
        circle = r[i]
        circles.put((circle[0],circle[1],circle[3]))
        i = i +1
    return circles

def bfs4neig(img,coordinate,label):
    q = qu.Queue()
    q.put(coordinate)
    counter = 0
    while not q.empty():
        p = q.get()
        counter += 1
        if img[p[0]][p[1]] == 255:
            img[p[0]][p[1]] = label
            if (p[0] > 0) and (img[p[0]-1][p[1]] == 255): #norte
                q.put((p[0]-1,p[1]))
        #    if (p[0] > 0) and (p[1] < img.shape[1]-1) and (img[p[0]-1][p[1]+1] == 255): #nordeste
        #        fila.put((p[0]-1,p[1]+1))
            if(p[1] < (img.shape[1]-1)) and (img[p[0]][p[1]+1] == 255): #leste
                q.put((p[0],p[1]+1))
        #    if(p[0] < (img.shape[0]-1)) and (p[1] < img.shape[1]-1) and (img[p[0]+1][p[1]+1] == 255): #sudeste
        #        fila.put((p[0]+1,p[1]+1))
            if(p[0] < (img.shape[0]-1)) and (img[p[0]+1][p[1]] == 255): #sul
                q.put((p[0]+1,p[1]))
        #    if(p[0] < (img.shape[0]-1)) and (p[1] > 0) and (img[p[0]+1][p[1]-1] == 255): #sudoeste
        #        fila.put((p[0]+1,p[1]-1))
            if(p[1] > 0) and (img[p[0]][p[1]-1] == 255): #oeste
                q.put((p[0],p[1]-1))
        #    if (p[0] > 0) and (p[1] > 0) and (img[p[0]-1][p[1]-1] == 255): #nordeste
        #        fila.put((p[0]-1,p[1]-1))
    return img,counter

def findObjects(img):
    label = 1
    while (np.min(img) == 0):
        coordinate = (np.where(img==0)[0][0], np.where(img==0)[1][0])
        img = bfs(img,coordinate,label)
        label+=1
        if label == 255:
            label+=1
    return img,label

def bfs(img,coordinate,label):
    q = qu.Queue()
    q.put(coordinate)
    while not q.empty():
        p = q.get()
        if img[p[0]][p[1]] == 0:
            img[p[0]][p[1]] = label
            if (p[0] > 0) and (img[p[0]-1][p[1]] == 0): #norte
                q.put((p[0]-1,p[1]))
            if (p[0] > 0) and (p[1] < img.shape[1]-1) and (img[p[0]-1][p[1]+1] == 0): #nordeste
                q.put((p[0]-1,p[1]+1))
            if(p[1] < (img.shape[1]-1)) and (img[p[0]][p[1]+1] == 0): #leste
                q.put((p[0],p[1]+1))
            if(p[0] < (img.shape[0]-1)) and (p[1] < img.shape[1]-1) and (img[p[0]+1][p[1]+1] == 0): #sudeste
                q.put((p[0]+1,p[1]+1))
            if(p[0] < (img.shape[0]-1)) and (img[p[0]+1][p[1]] == 0): #sul
                q.put((p[0]+1,p[1]))
            if(p[0] < (img.shape[0]-1)) and (p[1] > 0) and (img[p[0]+1][p[1]-1] == 0): #sudoeste
                q.put((p[0]+1,p[1]-1))
            if(p[1] > 0) and (img[p[0]][p[1]-1] == 0): #oeste
                q.put((p[0],p[1]-1))
            if (p[0] > 0) and (p[1] > 0) and (img[p[0]-1][p[1]-1] == 0): #nordeste
                q.put((p[0]-1,p[1]-1))
    return img

def crop(img,label):
    minX = np.min(np.where(img == label)[0])
    maxX = np.max(np.where(img == label)[0])
    minY = np.min(np.where(img == label)[1])
    maxY = np.max(np.where(img == label)[1])
    if(minX == maxX or minY == maxY):
        return img,False
    return img[minX:maxX,minY:maxY],True

def sizeEllipse(size):
    if size >= 10000:
        return 28
    return 21

def classifier(img):
    img,b = crop(img,0)
    obj = len(np.where(img == 0)[0])
    obj1 = len(np.where(img == 0)[1])
    x,y = img.shape

    if(x>y):
        ecc = x/y
        minnor = y
    else:
        ecc = y/x
        minnor = x
    sol = x*y / obj


def classifierArrow(img,label,av,med,t,numbers):

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
                numbers.append(label)
    return numbers
