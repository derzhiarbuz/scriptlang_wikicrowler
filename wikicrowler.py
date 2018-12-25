# -*- coding: utf-8 -*-
"""
Created on Mon Dec 24 18:56:05 2018

@author: Derzhiarbuz
"""
import re
import requests
import bs4
import pickle

v2 = 'BBC'
v1 = 'Sway_(book)'

V = {}          #dict ov vertices
F1 = set()      #set of vertices that can be reached from v1
T1 = set()      #set of vertices from wich v1 can be reached
F2 = set()      #set of vertices that can be reached from v2
T2 = set()      #set of vertices from wich v2 can be reached
Vpool1 = set()  #set of vertice names that should be downloaded, collected from v1 crawl
Vpool2 = set()  #set of vertice names that should be downloaded, collected from v2 crawl
Vqueue1 = []    #list of vertice names that should be downloaded, collected from v1 crawl (cause order nake sense)
Vqueue2 = []    #list of vertice names that should be downloaded, collected from v2 crawl (cause order nake sense)

v1v2path = []
v2v1path = []

#function to get page names for references on page with name p_name
def get_refs_for_page_name(p_name:str):
    req = requests.get("https://en.wikipedia.org/wiki/"+p_name)
    if req.status_code != 200: 
        return []
    soup = bs4.BeautifulSoup(req.text, features="lxml")
    cont = soup.findAll('div', attrs={'class':'mw-parser-output'})
    refs = []
    for div in cont:
        refs += re.findall(r'href="/wiki/([^:]*?)"',str(div))
    return set(refs)

def get_random_name():
    req = requests.get("https://en.wikipedia.org/wiki/Special:Random")
    if req.status_code != 200: 
        return ''
    return req.url.split('/').pop()

def empty_vertex():
    v = {}
    v['in'] = set()
    v['out'] = set()
    v['loaded'] = False
    return v

def save_state(fname:str):
    global Vpool1
    global Vpool2
    global Vqueue1
    global Vqueue2
    global F1
    global T1
    global F2
    global T2
    global V
    global v1
    global v2
    
    state = {}
    state['v1'] = v1
    state['v2'] = v2
    state['V'] = V
    state['F1'] = F1
    state['F2'] = F2
    state['T1'] = T1
    state['T2'] = T2
    state['Vqueue1'] = Vqueue1
    state['Vqueue2'] = Vqueue2
    state['Vpool1'] = Vpool1
    state['Vpool2'] = Vpool2
    
    file = open(fname,"wb")
    pickle.dump(state,file)
    file.close()

def load_state(fname:str): 
    global Vpool1
    global Vpool2
    global Vqueue1
    global Vqueue2
    global F1
    global T1
    global F2
    global T2
    global V
    global v1
    global v2
    
    state = {}
    try:
        file = open(fname, "rb")
        state = pickle.load(file)
        file.close()
    except IOError:
        print("Unable to open "+fname+"... do nothing")
    finally:
        v1 = state['v1']
        v2 = state['v2']
        V = state['V']
        F1 = state['F1']
        F2 = state['F2']
        T1 = state['T1']
        T2 = state['T2']
        Vqueue1 = state['Vqueue1']
        Vqueue2 = state['Vqueue2']
        Vpool1 = state['Vpool1']
        Vpool2 = state['Vpool2']

def add_vertex_to_F(vname:str, F:set):
    global V
    
    vtoadd = set()
    newvtoadd = set([vname])
    
    contin = True
    while contin:
        contin = False
        vtoadd = newvtoadd
        newvtoadd = set()
        for name in vtoadd:
            if name not in F:
                v = V.get(name)
                if v!=None:
                    newvtoadd.update(v['out'])
                    contin = True
                F.add(name)

def add_vertex_to_T(vname:str, T:set):
    global V
    
    vtoadd = set()
    newvtoadd = set([vname])
    
    contin = True
    while contin:
        contin = False
        vtoadd = newvtoadd
        newvtoadd = set()
        for name in vtoadd:
            if name not in T:
                v = V.get(name)
                if v!=None:
                    newvtoadd.update(v['in'])
                    contin = True  
                T.add(name)
        

def process_vpool(poolN):
    global Vpool1
    global Vpool2
    global Vqueue1
    global Vqueue2
    global F1
    global T1
    global F2
    global T2
    global V
    global v1
    global v2
    
    if poolN==1:
        mypool = Vpool1
        hispool = Vpool2
        myqueue = Vqueue1
        hisqueue = Vqueue2
        myF = F1
        myT = T1
        hisF = F2
        hisT = T2
        myv = v1
        hisv = v2
    else:
        mypool = Vpool2
        hispool = Vpool1
        myqueue = Vqueue2
        hisqueue = Vqueue1
        myF = F2
        myT = T2
        hisF = F1
        hisT = T1
        myv = v2
        hisv = v1
    
    name = ''
    while len(myqueue)>0 and len(name)==0:
        name = myqueue.pop(0)   #get oldest element, but first check if it haven't been downloaded yet
        if name not in mypool:
            name = ''
           
    if len(name)==0:        #if there is noo elements in pool to download, do nothing
        return 0
    
    print("processing "+name)
    
    myvertex = V.get(name)
    if myvertex == None:       #it should happen never, but God is unpredictable
        print('Vertex ws in Vpool'+str(poolN)+', but was not in V lol')
        myvertex = empty_vertex()
        V[name] = myvertex
        
    outnames = set()
    outnames = get_refs_for_page_name(name) #getting names of outgoing vertices
    myvertex['out'] = outnames              #and assign it to vertex OUT set
    inmyT = False
    inhisT = False
    for oname in outnames:
        overtx = V.get(oname)       #make sure new vertex is in set of all vertices, V (adding if not)
        if overtx == None:
            overtx = empty_vertex()
            V[oname] = overtx
            mypool.add(oname)
            myqueue.append(oname)
        overtx['in'].add(name)      #add myvertex to IN set of all vertices from myvertex OUT set
        #if there is edge from myvertex to myv or to vertex from myT, then in my T
        if oname == myv or oname in myT:
            inmyT = True  
        #if there is edge from myvertex to hisv or to vertex from hisT, then in his T
        if oname == hisv or oname in hisT:
            inhisT = True           
    
    #reorganize F1, F2 and make sure all inclusion rules are correct
    for oname in outnames:
        add_vertex_to_F(oname,myF)   #all outgoing vertices are in myF
    mypool.discard(name)
    if name in hisF:
        for oname in outnames:
            add_vertex_to_F(oname,hisF)
    hispool.discard(name)
    
    #reorganize T1, T2 and make sure all inclusion rules are correct
    if inmyT:
        add_vertex_to_T(name,myT)
    if inhisT:
        add_vertex_to_T(name,hisT)
        
def find_path_in_FTset(FTset:set, vf:str, vt:str):
    global V
    
    lengths = {}
    FTset.add(vf)
    FTset.add(vt)
    lengths[-1] = set(FTset)
    lengths[0] = set()
    lengths[0].add(vf)
    lengths[-1].discard(vf)
    i=1
    notfinished = True
    while len(lengths[-1]) and notfinished and i<50:
        lengths[i] = set()
        for vn in lengths[i-1]:
            v = V[vn]
            for vnn in v['out']:
                if vnn in lengths[-1]:
                    lengths[i].add(vnn)
                    lengths[-1].discard(vnn)
                    if vnn == vt:
                        notfinished = False
        i+=1
    
    path = [vt]
    for j in range(2,i):
        v = V[path[0]]
        path.insert(0,(v['in']&lengths[i-j]).pop())
    path.insert(0,vf)
    return path
    

if __name__ == '__main__':

    v1 = get_random_name()
    v2 = get_random_name()
    print("From: " + str(v1))
    print("To: " + str(v2))
    
    if len(Vpool1)==0:
        Vqueue1 = [v1]
        Vpool1 = set(Vqueue1)
    if len(Vpool2)==0:
        Vqueue2 = [v2]
        Vpool2 = set(Vqueue2)
    
    #3load_state("test.pkl")    
    #print("F1&T2 = " + str(F1&T2))
    #print("F2&T1 = " + str(F2&T1))
    #print(find_path_in_FTset(F2&T1, v2, v1))
    for i in range(1000):
        process_vpool(1)
        process_vpool(2)

        if len(v1v2path) == 0:
            int12 = F1&T2
            if len(int12):
                v1v2path = find_path_in_FTset(F1&T2, v1, v2)
                print("F1&T2 = " + str(int12))
            else:
                print("F1&T2 is empty")
        if len(v1v2path) > 0:
            print("v1 -> v2 len: " + str(len(v1v2path)) + " path: " + str(v1v2path))
            
        if len(v2v1path) == 0:
            int21 = F2&T1
            if len(int21):
                v2v1path = find_path_in_FTset(F2&T1, v2, v1)
                print("F2&T1 = " + str(int21))
            else:
                print("F2&T1 is empty")
        if len(v2v1path) > 0:
            print("v2 -> v1 len: " + str(len(v2v1path)) + " path: " + str(v2v1path))

        print("Iteration "+str(i))
#        if len(F2&T1):
#            find_path_in_FTset(F2&T1, v2, v1)
        print("\n")
        if len(v1v2path)>0 and len(v2v1path)>0:
            print("\nResult\n")
            print("v1 -> v2 len: " + str(len(v1v2path)) + " path: " + str(v1v2path))
            print("\nv2 -> v1 len: " + str(len(v2v1path)) + " path: " + str(v2v1path))
            print("\ntotal requests made: " + str(i*2))
            break
        #time.sleep(0.2)
    save_state("test.pkl")
    