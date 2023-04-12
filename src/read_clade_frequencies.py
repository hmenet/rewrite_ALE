#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 14:19:06 2020

@author: hmenet
"""





import arbre
from rec_classes import Amalgamated_tree

#clades are implemented in a hashable type to be used with a dictionary as tuples of sorted leaves

#idea of the algorithm
#1 : in the gene tree, we do not look at the nodes but at the set of leaves of the node
#2 a clade does not have 2 children, but multiple possible couple of children, possible bipartition 
#3 we associate to each clade the frequencies of all bipartitions seen in the sample

def sorted_common_leaves_from_tree(tree):
    l=tree.leaves_unrooted()
    l_leaves=[i.name for i in l]
    l_leaves.sort()
    return l_leaves

def sorted_common_leaves_from_leaves(leaves):
    l_leaves=[i.name for i in leaves]
    l_leaves.sort()
    return l_leaves


#clades are numbered, starting at 0

#try to add a clade, if not present
#tree_clade : a tree, the clade will be its leaves
#a clade is just an index, in clade_elements[clade] : sorted list of leaves corresponding to the clade
#and the leaves are the leaves names
def clade_from_tree(tree_clade, clade_elements, clade_keys):
    n_clade=len(clade_elements)
    leaves_clade=tuple(sorted_common_leaves_from_tree(tree_clade))
    clade=-1
    if leaves_clade in clade_keys:
        clade=clade_keys[leaves_clade]
    else:
        clade=n_clade
        clade_elements[clade]=leaves_clade
        clade_keys[leaves_clade]=clade
    return clade

def clade_from_leaves(leaves_clade, clade_elements, clade_keys):
    n_clade=len(clade_elements)
    leaves_clade=tuple(sorted_common_leaves_from_leaves(leaves_clade))
    clade=-1
    if leaves_clade in clade_keys:
        clade=clade_keys[leaves_clade]
    else:
        clade=n_clade
        clade_elements[clade]=leaves_clade
        clade_keys[leaves_clade]=clade
    return clade


#clade_frequencies[u][(v,w)]=0# bipartition v w knowing bipartition u \bar{u}
#l_tree : list of tree on which we want the clade frequencies
#for each bipartitions, 3 possible roots.


def partition_counter_one_tree(tree, clade_elements, clade_keys, bipartition_number, tripartition_number):
    #if rooted, we unroot
    if tree.right2==None:
        arbre.from_rooted_to_un(tree)
    tree_post_order = tree.post_order_traversal_unrooted()
    all_leaves=tree.leaves_unrooted()
    clade1=clade_from_leaves(all_leaves, clade_elements, clade_keys)#clade 0 is the clade of all leaves
    for e in tree_post_order:
        if not e.isRoot():
            #we cut the edge between e and its parent to create a bipartition
            c1=e.leaves_unrooted()#first half of the bipartition
            c2=[leaf for leaf in all_leaves if not leaf in c1]
            clade1=clade_from_leaves(c1, clade_elements, clade_keys)
            clade2=clade_from_leaves(c2, clade_elements, clade_keys)
            bipartition=(min(clade1, clade2), max(clade1, clade2))
            tmp_compte_a_prendre=1
            if bipartition in bipartition_number:
                bipartition_number[bipartition]+=tmp_compte_a_prendre
            else:
                bipartition_number[bipartition]=tmp_compte_a_prendre

        #now, we count the tripartitions generated by deleting the considered node
        #deleting leaves and root do not create tripartitions
        if not e.isLeaf():
            #we already computed one of the clades, c2
            #we now compute the remaining 2
            if not e.isRoot():
                child_clade1=clade_from_tree(e.left, clade_elements, clade_keys)
                child_clade2=clade_from_tree(e.right, clade_elements, clade_keys)
                child_clade3=clade2
            else:
                #if its the root, no clades have been computed
                child_clade1=clade_from_tree(e.left, clade_elements, clade_keys)
                child_clade2=clade_from_tree(e.right, clade_elements, clade_keys)
                child_clade3=clade_from_tree(e.right2, clade_elements, clade_keys)
            l_tmp=[child_clade1, child_clade2, child_clade3]
            l_tmp.sort()
            c1_tmp, c2_tmp,c3_tmp=l_tmp
            tripartition=c1_tmp, c2_tmp,c3_tmp
            if tripartition in tripartition_number:
                tripartition_number[tripartition]+=1
            else:
                tripartition_number[tripartition]=1

#return the clade corresponding to the union of the two input clades
def union_clade(c1,c2,clade_elements, clade_keys):
    l=list(clade_elements[c1])
    l+=list(clade_elements[c2])
    l.sort()
    c=clade_keys[tuple(l)]
    return c


#trees are unrooted
def compute_clade_frequencies(l_tree):
    bipartition_number=dict()
    tripartition_number=dict()
    clade_elements=dict()
    clade_keys=dict()
    #union_clade=dict()
    kcmpt=0
    for tree in l_tree:
        kcmpt+=1
        partition_counter_one_tree(tree, clade_elements, clade_keys,bipartition_number, tripartition_number)
    clade_frequencies=dict()
    n_clade=len(clade_elements)
    for c in range(n_clade):
        clade_frequencies[c]=dict()
    for c1,c2,c3 in tripartition_number:
        #to be faster we would have to keep in memory the relations between the clades 
        n_tripartition=tripartition_number[(c1,c2,c3)]
        #a1 a2 knowing a, and ab represent \bar{a}
        for tmp1,tmp2,tmp3 in [(c2,c3,c1),(c1,c3,c2),(c1,c2,c3)]:
            #a,a1,a2,ab = union_clade[(min(tmp1,tmp2), max(tmp1,tmp2))],tmp1,tmp2,tmp3
            #print("a")

            a,a1,a2,ab = union_clade(tmp1,tmp2,clade_elements, clade_keys),tmp1,tmp2,tmp3
            b_continue=True
            for u in [a,a1,a2]:
                if len(clade_elements[u])==0:
                    b_continue=False
            if b_continue:
                clade_frequencies[a][(min(a1,a2),max(a1,a2))]=n_tripartition/bipartition_number[(min(a,ab),max(a,ab))]
    #for the bipartition frequency of the first clade, there is no knowing, no tripartition
    s=sum([bipartition_number[u] for u in bipartition_number.keys()])
    for c1,c2 in bipartition_number:
        clade_frequencies[0][(min(c1,c2),max(c1,c2))]=bipartition_number[(min(c1,c2),max(c1,c2))]/s

    amalgamated_tree=Amalgamated_tree()
    amalgamated_tree.initialize(clade_elements,clade_frequencies)
    return amalgamated_tree


def compute_clade_frequencies_multiple_families(l_tree_by_family):
    am_tree_list=[]
    for l_tree in l_tree_by_family:
        amalgamated_tree=compute_clade_frequencies(l_tree)
        #tree list are given as "name"+str(id_counter)
        am_tree_list.append(amalgamated_tree)
    return am_tree_list

def from_rooted_tree_to_clades(tree):
    clade_elements=dict()
    clade_keys=dict()
    clade_frequencies=dict()
    tree_to_clade=dict()
    clade_to_tree=dict()
    c=0
    for e in tree.post_order_traversal():
        l_tmp=[u.name for u in e.leaves()]
        l_tmp.sort()
        leaves = tuple(l_tmp)
        clade_elements[c]=leaves
        clade_keys[leaves]=c
        tree_to_clade[e]=c
        clade_to_tree[c]=e
        if not e.isRoot():
            p=e.parent
            pl_tmp=[u.name for u in p.leaves()]
            pl_tmp.sort()
            pleaves=tuple(pl_tmp)
            pc=clade_keys[pleaves]
            cl_tmp=[u.name for u in p.left.leaves()]
            cr_tmp=[u.name for u in p.right.leaves()]
            cl_tmp.sort()
            cr_tmp.sort()
            clleaves=tuple(cl_tmp)
            crleaves=tuple(cr_tmp)
            if clleaves in clade_keys and crleaves in clade_keys:
                cl=clade_keys[clleaves]
                cr=clade_keys[crleaves]
                clade_frequencies[pc]=dict()
                clade_frequencies[pc][(min(cl,cr), max(cl,cr))]=1
        if e.isLeaf():
            clade_frequencies[c]=dict()
        c+=1

    amalgamated_tree=Amalgamated_tree()
    amalgamated_tree.initialize(clade_elements,clade_frequencies,corresponding_clade_to_tree=clade_to_tree)

    return amalgamated_tree

#from rooted tree to clades data list, with no amalgamation or root uncertainty, for the intermediate level of 3 level reconciliation
def compute_clade_frequencies_rooted_tree(l_tree_by_family):
    am_tree_list=[]
    for tree in l_tree_by_family:
        am_tree_list.append(from_rooted_tree_to_clades(tree))
    return am_tree_list





