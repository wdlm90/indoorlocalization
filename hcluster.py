#coding:UTF-8
#Hierarchical clustering 层次聚类
from dtw import dtw
import numpy as np
class bicluster:
    def __init__(self, vec, left=None,right=None,distance=0.0,id=None):
        self.left = left
        self.right = right  #每次聚类都是一对数据，left保存其中一个数据，right保存另一个
        self.vec = vec      
        self.id = id     
        self.distance = distance
def showcluster(cluster):
    if cluster.left==None and cluster.right ==None:
        return [cluster.id]
    return showcluster(cluster.left) + showcluster(cluster.right)
def cluster_distance(cluster1,cluster2):
    veclist1 = cluster1.vec
    veclist2 = cluster2.vec
    dislist = []
    for vec1 in veclist1:
        for vec2 in veclist2:
            distance,cost,path = dtw(vec1,vec2)
            dislist.append(distance)
    return np.mean(dislist)
            
            

def hcluster(blogwords,n) :
    biclusters = [ bicluster(vec =[blogwords[i]], id = i ) for i in range(len(blogwords)) ]
    distances = {}
    flag = None;
    currentclusted = -1
    while(len(biclusters) > n) : #假设聚成n个类
        min_val = float("inf"); #Python的无穷大应该是inf
        biclusters_len = len(biclusters)
        for i in range(biclusters_len-1) :
            for j in range(i + 1, biclusters_len) :
                if distances.get((biclusters[i].id,biclusters[j].id)) == None:
                    distances[(biclusters[i].id,biclusters[j].id)] =\
                    cluster_distance(biclusters[i],biclusters[j])
                d = distances[(biclusters[i].id,biclusters[j].id)] 
                if d < min_val :
                    min_val = d
                    flag = (i,j)
        bic1,bic2 = flag #解包bic1 = i , bic2 = j
        newvec = biclusters[bic1].vec + biclusters[bic2].vec
        #newvec = [(biclusters[bic1].vec[i] + biclusters[bic2].vec[i])/2 for i in range(len(biclusters[bic1].vec))]
        newbic = bicluster(newvec, left=biclusters[bic1], right=biclusters[bic2], distance=min_val, id = currentclusted) #二合一
        currentclusted -= 1
        del biclusters[bic2] #删除聚成一起的两个数据，由于这两个数据要聚成一起
        del biclusters[bic1]
        biclusters.append(newbic)#补回新聚类中心
        clusters = [showcluster(biclusters[i]) for i in range(len(biclusters))] #深度优先搜索叶子节点，用于输出显示
    return biclusters,clusters
