
from arbre import Tree

import numpy as np

############

class Event_rates:
    def __init__(self, tr=0.01,lr=0.01,dr=0.01):
        self.tr=tr #transfer rate
        self.dr=dr #duplication rate
        self.lr=lr #loss rate
        self.sr_compute() #speciation rate, ensuring sum of rates equal to 1
        self.log_rates()

    def log_rates(self): #initialize log rates for computation in log space
        self.ltr=np.log(self.tr)
        self.ldr=np.log(self.dr)
        self.llr=np.log(self.lr)
        self.lsr=np.log(self.sr)

    def sr_compute(self):
        self.sr=1-self.tr - self.dr - self.lr #speciation rate, ensuring sum of rates equal to 1

    def reinit(self):#recompute speciation rate and log rates, to use after modification of one of the rate
        self.sr_compute()
        self.log_rates()

    def pp(self):
        return "S " + self.sr + "D " + self.dr + "T " + self.tr + "L " + self.lr

#############

class Tree_list:
    def __init__(self,t_list):
        self.tree_list=t_list
        self.post_order_traversal()
        self.first_element=t_list[0]

    def post_order_traversal(self):
        post_order=[]
        for tree in self.tree_list:
            for u in tree.post_order_traversal():
                post_order.append(u)
        self.post_order=post_order

##############

P, P_TL,E, parasite_post_order, clades_data, rates_g,c_match_list_i_clade, log_l, corr_size,best,i, return_r, P_transfer,ncpu=entry_tuple

parasite_post_order,E, Eavg_no_log, clades_data, rates_g, c_match_list_i_clade, best, multi_process, multi_process_family, sample, n_sample, return_r, P_transfer,ncpu = entry_tuple


class Rec_upper_tree_computation:
    def __init__(self):
        self.E=None
        self.Eavg_no_log=None
        P_transfer=None

class Rec_lower_tree_computation:
    def __init__(self):
        self.P=None
        self.P_TL=None
        self.log_l=None
        self.corr_size=None

##############

class Rec_problem:
    def __init__(self, symb_list,amal_genes):
        self.upper = symb_list
        self.lower = amal_genes
        self.single_lower=None
        self.output_path = "output/"
        self.n_sample = 100
        self.n_steps = 5
        self.n_rec_sample_rates = 100
        self.n_output_scenario=10
        self.best_rec = False
        self.rates = Event_rates(tr=0.01,lr=0.01,dr=0.01)
        self.ncpu = 4
        self.multiprocess_fam=False
        self.multiprocess_sampling=False
        self.upper_tree_computation=None
        self.lower_tree_computation=None
        self.rate_inference=False #True when infering rates

        ### for three level rec
        self.third_level=False
        self.upper_rec=None
        self.heuristic=None
        self.mc_samples=10




    def __iter__(self):
        self.iter_lower=0
        return self

    def __next__(self):
        if self.iter_lower<len(self.lower):
            single_gene_rec=Rec_problem(self.upper,None)
            single_gene_rec.single_lower=self.lower[iter_lower]
            single_gene_rec.n_sample = self.n_sample
            single_gene_rec.n_steps = self.n_steps
            single_gene_rec.n_rec_sample_rates = self.n_rec_sample_rates
            single_gene_rec.n_recphyloxml= self.n_recphyloxml
            single_gene_rec.best_rec = self.best_rec
            single_gene_rec.rates = self.rates
            single_gene_rec.ncpu = self.ncpu
            single_gene_rec.multiprocess_fam= self.multiprocess_fam
            single_gene_rec.multiprocess_sampling= self.multiprocess_sampling
            single_gene_rec.upper_tree_computation= self.upper_tree_computation
            single_gene_rec.third_level=self.third_level
            single_gene_rec.upper_rec=self.upper_rec
            single_gene_rec.heuristic=self.heuristic
            single_gene_rec.mc_samples=self.mc_samples

            self.iter_lower+=1e
            return single_gene_rec
        else:
            raise StopIteration





#################

class Amalgamated_tree:
    def __init__(self):
        self.clade_leaves=None
        self.child_frequencies=None
        self.tree_name=None
        self.match=None
        self.corresponding_tree=None
        self.reverse_post_order=None
        self.leaves=None
        self.constant_match=None

    def aux_init(self,clade_elements,clade_frequencies,clade_id,d,corresponding_clade_to_tree=None):
        self.clade_leaves=clade_elements[clade_id]
        if not corresponding_clade_to_tree is None:
            self.corresponding_tree=corresponding_clade_to_tree(clade_id)
        new_clade_frequencies=dict()
        for (cl,cr) in clade_frequencies[clade_id]:
            new_cs=[]
            for c in [cl,cr]:
                if not c in d:
                    new_c=Amalgamated_tree()
                    new_c.aux_init(clade_elements,clade_frequencies,c,d)
                    d[c]=new_c
                else:
                    new_c=d[c]
                new_cs.append(new_c)
            newcl,newcr=new_cs
            new_clade_frequencies[(newcl,newcr)]=clade_frequencies[clade_id][(cl,cr)]
        self.child_frequencies=new_clade_frequencies

    def initialize(self,clade_elements,clade_frequencies,corresponding_clade_to_tree=None):
        d=dict()
        d[0]=self
        self.aux_init(clade_elements,clade_frequencies,0,d,corresponding_clade_to_tree=corresponding_clade_to_tree)
        self.reverse_post_order_traversal()
        self.leaves_traversal()
        self.log_freq()

    def is_leaf(self):
        return(len(clade_leaves))==1

    def aux_liste(self,l,d):
        for (cl,cr) in self.child_frequencies:
            for c in [cl,cr]:
                if not c in d:
                    d[c]=0
                    l.append(c)
                    c.aux_liste(l,d)

    def liste(self):
        d=dict()
        l=[self]
        self.aux_list(l,d)
        return l

    def reverse_post_order_traversal(self):
        def order_clade(clade):
            return(len(clade.clade_leaves))
        l=self.liste()
        l.sort(key=order_clade, reverse=True)
        #ordre donné par la taille des clades est bien un ordre qui empeche les fils d'apparaitre avant leur parent
        self.reverse_post_order=l
        return l

    def leaves_traversal(self):
        if self.reverse_post_order is None:
            self.reverse_post_order_traversal()
        l=[u for u in self.reverse_post_order if u.is_leaf()]
        self.leaves=l
        return l

    def leaves(self):
        if self.leaves is None:
            return self.leaves_traversal()
        else:
            return self.leaves

    #compute log of the frequencies
    def log_freq(self):
        for clade in self.reverse_post_order:
            log_d=dict()
            for k in clade.child_frequencies:
                log_d[k]=np.log(clade.child_frequencies[k])
            clade.log_child_frequencies=log_d

    def save_match(self):
        for clade in self.reverse_post_order:
            clade.constant_match=clade.match


##################$$


class Rec_event:
    def __init__(self):
        self.name=None
        self.lower=None
        self.lower_left=None
        self.lower_right=None
        self.upper=None
        self.upper_left_or_keeper_or_receiver=None
        self.upper_right_or_loser_or_donor=None
        self.upper_match=None
        self.upper_left_match=None
        self.upper_right_match=None

    def is_third_level(self):
        return self.upper_match is None

    def key(self):
        l=[self.name, self.upper.name, self.upper_left_or_keeper_or_receiver.name, self.upper_right_or_loser_or_donor.name,self.lower,self.lower_left,self.lower_right]
        if self.is_third_level():
            l.append(self.upper_match)
            l.append(self.upper_left_match)
            l.append(self.upper_right_match)
        return(tuple(l))



class Rec_scenario:
    def __init__(self):
        self.event_list=[]
        self.reconstructed_lower=Tree()
        self.reconstructed_lower.event_list=[]
        self.log_likelihood=0
        self.am_tree_to_reconstructed_tree=dict()

#l_scenario is a list of reconstructed_tree
class Rec_sol:
    def __init__(self,log_likelihood,l_event_aggregate,l_scenario):
        self.log_likelihood=log_likelihood
        self.l_event_aggregate=l_event_aggregate
        self.l_scenario=l_scenario
        self.upper_divided_sol=None

    def aggregate_from_scenario_list(self,scenario_list):
        l_event_aggregate=[]
        #we traverse all lower families
        for scenario in scenario_list:
            d=dict()


    def from_upper_divided_to_global(self):
        for rec_sol in upper_divided_sol:



