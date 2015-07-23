import pandas as pd
import numpy as np

# Define Gower similarity metric for a single row.
def gower_similarity(data_df,ref_df):

    # Set up data structures
    feature_names = ref_df.columns
    nFeatures = len(feature_names)
    sim = np.empty([nFeatures,1]) # each feature's similarity index (in [0, 1])
    wgt = np.empty([nFeatures,1]) # weight to put on each feature (0 or 1)

    # Find similarity for each feature
    # 'any' is only used for correct syntax -- each comparison is on a single number
    # 'np.sum' is used to convert series with a single number into scalar
    for idx in range(len(feature_names)):
        col = feature_names[idx]
        if ref_df[col].dtype == 'bool':
            sim[idx] = any(ref_df[col] == True) and data_df[col] == 1
            wgt[idx] = any(ref_df[col] == True) or data_df[col] == 1
        elif ref_df[col].dtype in ['float', 'int']:
            sim[idx] = 1 - np.absolute(np.sum(ref_df[col]) - np.sum(data_df[col]))
            wgt[idx] = any(np.isfinite(ref_df[col])) and np.isfinite(data_df[col])
        else:
            print "error"
            
    # Find and return overall similarity
    return np.nansum(sim) / np.nansum(wgt)

# Rank programs based on criteria specified by user.
# Assume ideal_org consists of only the features of interest.
def rank_programs(fulldf = pd.DataFrame(np.empty([0,0])), ideal_org = pd.DataFrame(np.empty([0,0]))):
    # Check input
    if fulldf.empty:
        return fulldf

    # Set up parameters
    max_output = 10 # number of organizations to print
    feature_names = ideal_org.columns

    # Make simpler dataframe with only the relevant fields
    reduceddf = fulldf[:][feature_names]

    # Normalize values
    for col in feature_names:
        minval = np.min([np.min(ideal_org[col]), np.min(reduceddf[col])])
        ideal_org[col] -= minval
        reduceddf[col] -= minval
        maxval = np.max([np.max(ideal_org[col]), np.max(reduceddf[col])])
        ideal_org[col] /= maxval
        reduceddf[col] /= maxval

    # Find distances for all charities
    dists = pd.Series(index=reduceddf.index, name='gower')
    for idx, r in reduceddf.iterrows():
        dists[idx] = gower_similarity(r, ideal_org)

    # Merge distances with other data
    fulldf['gower'] = dists   

    # Find best charities based on distance metric.
    fulldf.sort(columns='gower', ascending=False, inplace=True)
    fulldf['rank'] = range(1,len(fulldf)+1)
    top_charities = fulldf[:max_output]

    return top_charities


