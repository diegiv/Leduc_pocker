from sklearn.cluster import KMeans
from Game import *
import pandas as pd
import copy

def abstract(game, cl1, cl2):

    # Setta gli offset per tutti i nodi foglia
    offset = 14
    for n in game.nodes:
        if type(game.nodes[n]) is LeafNode:
            game.nodes[n].payoffs[0] += offset
            game.nodes[n].payoffs[1] += offset

    # Seleziona tutti gli infoset del giocatore 1 (1° livello)
    sets = []
    for i in game.infosets:
        x = str(i)
        if len(x)==3 and x[2] == '?':
            sets.append(i)

    # Seleziona tutti gli infoset del giocatore 2 (2° livello)
    sets2 = []
    for i in game.infosets:
        x = str(i)
        if x.count('/') == 2 and x[1] == '?':
            sets2.append(i)

    # Seleziona tutti i leaf node appartenti ad un infoset (del player1)
    mydict = {k:[] for k in sets}
    for n in game.nodes:
        if type(game.nodes[n]) is LeafNode :
            for s in sets:
                if str(n).startswith(s.replace('/','/C:').replace('?','')) :
                    mydict[s].append(n)

    # Seleziona tutti i leaf node appartenti ad un infoset (del player2)
    mydict2 = {k:[] for k in sets2}
    for n in game.nodes:
        if type(game.nodes[n]) is LeafNode :
            for s in sets2:
                s1 = s.replace('/','/C:')
                if str(n)[4]==s1[4] :
                    mydict2[s].append(n)

    # Crea colonne per il dataset del primo kmeans
    columns = {}
    for s in sets:
        for k in mydict[s]:
            k = k[:3] + '*' + k[4:]
            columns[k] = []
    
    # Crea colonne per il dataset del secondo kmeans
    columns2 = {}
    for s in sets2:
        for k in mydict2[s]:
            k = k[:4] + '*' + k[5:]
            columns2[k] = []

    for j, key in enumerate(mydict):
        for x in mydict[key]:
            y = x[:3] + '*' + x[4:]
            columns[y].append(game.nodes[x].payoffs[0])
        for c in columns:
            if len(columns[c])==j:
                columns[c].append(0)

    for j, key in enumerate(mydict2):
        for x in mydict2[key]:
            y = x[:4] + '*' + x[5:]
            columns2[y].append(game.nodes[x].payoffs[0])
        for c in columns2:
            if len(columns2[c])==j:
                columns2[c].append(0)

    df = pd.DataFrame(data=columns, index=sets)
    df.sort_index(inplace=True)
    # print(df.head())
    kmeans = KMeans(n_clusters=cl1, random_state=0).fit(df)
    pred = kmeans.predict(df)
    # print(pred)

    df2 = pd.DataFrame(data=columns2, index=sets2)
    df2.sort_index(inplace=True)
    drop_list = list(filter(lambda x: str.endswith(x,'/P1:raise2'), sets2))
    df2 = df2.drop(drop_list)
    # print(df2.head(10))
    kmeans2 = KMeans(n_clusters=cl2, random_state=0).fit(df2)
    pred2 = kmeans2.predict(df2)
    #print(pred2)

    clust = {k:[] for k in pred}
    for i,p in enumerate(pred):
        clust[p].append(df.index[i])

    clust2 = {k:[] for k in pred2}
    clust3 = {k:[] for k in pred2}
    for i,p in enumerate(pred2):
        clust2[p].append(df2.index[i])
        clust3[p].append(df2.index[i].replace('c','raise2'))

    new_infosets = {}
    possible_names = ['α','β','χ','δ','ε','φ','γ','η','ι','λ','μ','ν','ο']
    possible_names2 = ['A','B','C','D','E','F','G','H','I','L','M','N','O']
    possible_names3 = copy.copy(possible_names2)
    
    clusters = {}
    for c in clust:
        clusters[possible_names.pop()] = clust[c]

    clusters2 = {}
    for c in clust2:
        clusters2[possible_names2.pop()] = clust2[c]

    clusters3 = {}
    for c in clust3:
        clusters3[possible_names3.pop()] = clust3[c]

    for c in clusters:
        x = clusters[c]
        for i in game.infosets:
            if i.startswith(x[0]):
                if len(x) > 1:
                    nodes = []
                    for j in x:
                        nodes.append(game.infosets[i.replace(x[0],j)].nodes)
                    nodes = [item for sublist in nodes for item in sublist]
                    mapping = []
                    for m in x:
                        mapping.append(game.infosets[i.replace(x[0],m)])
                    z = InfoSet(i.replace(x[0],'/'+c+'?'), nodes)
                    z.setMapping(mapping)
                    new_infosets[z.history] = z
                else:
                    new_infosets[i] = game.infosets[i]
                    new_infosets[i].setMapping([new_infosets[i]])

    def clusterize_2nd_pl(myclusters):
        for c in myclusters:
            x = myclusters[c]
            ##print(x)
            for i in game.infosets:
                if i.startswith(x[0]):
                    if len(x) > 1:
                        nodes = []
                        for j in x:
                            if i.replace(x[0],j) in game.infosets.keys():
                                nodes.append(game.infosets[i.replace(x[0],j)].nodes)
                        nodes = [item for sublist in nodes for item in sublist]
                        mapping = []
                        for m in x:
                            st = i.replace(x[0],m)
                            if st in game.infosets.keys():
                                mapping.append(game.infosets[st])                 
                        z = InfoSet(i.replace(x[0],'/?'+c), nodes)
                        z.setMapping(mapping)
                        new_infosets[z.history] = z
                    else:
                        new_infosets[i] = game.infosets[i]
                        new_infosets[i].setMapping([new_infosets[i]])
            
    clusterize_2nd_pl(clusters2)
    clusterize_2nd_pl(clusters3)

    for n in game.nodes:
        if type(game.nodes[n]) is LeafNode:
            game.nodes[n].payoffs[0] -= offset
            game.nodes[n].payoffs[1] -= offset

    new_game = GameTree(game.nodes, new_infosets)
    return new_game