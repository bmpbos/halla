#!/usr/bin/env python

"""
HAllA's Clustering using hierarchical clustering and Silhouette score 
To Run: 
$ ./hallaclust.py -i <distance_martix.txt> -o <clustering_output.txt>

"""

import argparse
import sys
import tempfile
import os
import shutil
import re
import pandas as pd
from scipy.cluster.hierarchy import to_tree, linkage
from numpy import array
try:
    from . import plot, hierarchy
except ImportError:
    sys.exit("CRITICAL ERROR: Unable to find the hierarchy module." + 
        " Please check your halla install.")
from . import config
from . import parser

def resoltion_hclust(data=None, distance_matrix=None,
                      number_of_estimated_clusters = None ,
                      linkage_method = 'single', output_dir=None, do_plot = False, resolution = 'high'):
    bTree=True
    if len(distance_matrix) > 0:
        D = distance_matrix
    elif  len(data) > 0 :
        D = pdist(data, metric=distance.pDistance)
    else:
        sys.exit("Warning! dataset or distance matrix must be provides!")
  
    if do_plot:
        Z = plot.heatmap(data_table = None , D = D, xlabels_order = [], xlabels = distance_matrix.index, 
                     filename= output_dir+"/hierarchical_heatmap", colLable = False, method =linkage_method, scale ='log') 
    else:
        Z = Z = linkage(D, method= linkage_method)
    import scipy.cluster.hierarchy as sch
    hclust_tree = to_tree(Z) 
    #clusters = cutree_to_get_below_threshold_number_of_features (hclust_tree, t = estimated_num_clust)
    if number_of_estimated_clusters == None:
        number_of_estimated_clusters,_ = hierarchy.predict_best_number_of_clusters(hclust_tree, distance_matrix)
    clusters = hierarchy.get_homogenous_clusters_silhouette(hclust_tree, array(D),
                                                            number_of_estimated_clusters= number_of_estimated_clusters,
                                                            resolution= resolution)
    #print [cluster.pre_order(lambda x: x.id) for cluster in clusters]
    return clusters

def parse_arguments(args):
    """ 
    Parse the arguments from the user
    """
    
    parser = argparse.ArgumentParser(
        description= "HAllA's Clustering using hierarchical clustering and Silhouette score.\n",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-v","--verbose", 
        help="additional output is printed\n", 
        action="store_true",
        default=False)
    parser.add_argument(
        "-i","--input",
        help="the input file D*N, Rows: D features and columns: N samples \n",
        required=False)
    parser.add_argument(
        "-d","--distance_matrix",
        help="the distance matrix file D*D (if input file is not provided), Rows: D features and columns: N samples \n",
        required=False)
    parser.add_argument(
        "-o","--output",
        help="the output directory\n",
        required=True)
    parser.add_argument(
        "-m", "--similarity_method",
        default= 'spearman',
        help="similarity measurement {default spearman, options: spearman, nmi, ami, dmic, mic, pearson, dcor}")
    parser.add_argument(
        "-n", "--estimated_number_of_clusters",
        type=int,
        help="estimated number of clusters")
    parser.add_argument(
        "-c","--linkage_method", 
        default= 'single',
        help="linkage clustering method method {default = single, options average, complete\n")
    parser.add_argument(
        "--plot", 
        help="dendrogram plus heatmap\n", 
        action="store_true",
        default=False)
    parser.add_argument(
        "--resolution", 
        default= 'high',
        help="high resolution enforce clusters to be smaller than n/log2(n) where n is the number of total features. Low resolution is good when w have well separated clusters.")

    return parser.parse_args()


def main( ):
    # Parse arguments from command line
    args=parse_arguments(sys.argv)
    config.similarity_method = args.similarity_method
    output_dir= args.output+"/"
    config.similarity_method = args.similarity_method
    df_distance = pd.read_table(args.distance_matrix, header=0, index_col =0)
    #df_distance = stats.scale_data(df_distance, scale = 'log')
    
    # write the results into outpute
    if os.path.isdir(output_dir):
        try:
            shutil.rmtree(output_dir)
        except EnvironmentError:
            sys.exit("Unable to remove directory: "+output_dir)
    
    # create new directory
    try:
        os.mkdir(output_dir)
    except EnvironmentError:
        sys.exit("Unable to create directory: "+output_dir)
    
    clusters = resoltion_hclust(distance_matrix=df_distance, 
                                number_of_estimated_clusters = args.estimated_number_of_clusters ,
                                linkage_method = args.linkage_method,
                                output_dir = output_dir,  do_plot = args.plot, resolution= args.resolution )
    
    f = open(output_dir+"/hallaclust.txt", 'w')
    print "There are %s clusters" %(len(clusters))
    for i in range(len(clusters)):
        f.write("cluster"+str(i+1)+"\t")
        features = clusters[i].pre_order(lambda x: x.id)
        feature_names = [df_distance.index[val] for val in features]
        for item in feature_names:
            f.write("%s " % item)
        
        f.write("\n")
    print "Output is written in " + args.output+"/hallaclust.txt"

        
if __name__ == "__main__":
    main( )