"""
This script will do:
1. read data from land_use maps (both change and existng)
2. read data from attraction maps
3. read
4. prepare the data in the format for curve fitting
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from optparse import OptionParser

LUDATA = "./LU_Maps/2001asc.txt"
LUCDATA = "./LU_Maps/2001_2006asc.txt"

POPDATA = "./Attraction_Value/attrmap-pop.txt"
EMPDATA = "./Attraction_Value/attrmap-emp.txt"
TRANSDATA = "./Attraction_Value/transport_att.txt"
SLOPEDATA = "./Attraction_Value/slope_cost.txt"
BNDDATA = "./Other_Maps/boundary.txt"
NOGODATA = "./Other_Maps/no_growth.txt"

RESOUT = "./Output/resout.txt"
COMOUT = "./Output/comout.txt"


'''
Deciding change LU or exsting LU
'''
def opt_parser():

    parse = OptionParser()
    #attraction map option
    parse.add_option('-c', '--change', metavar='CENTERTYPE', default=False,
                    help='1 for change and 0 for no change') # change or existing option

    opts, args = parse.parse_args()
    ischg = 0
    opts, args = parse.parse_args()
    if not opts.change:
        ischg = 0
        print "No change or existing given. Default to be no change"
    elif opts.change == "0":
        ischg = 0
    elif opts.change == "1":
        ischg = 1
    else:
        parse.error("-c option needs to be either 1 or 0")

    return ischg

'''
Load Data
'''
def data_loader(ischg):
    if ischg == 0:
        lu_data = pd.read_csv(LUDATA, sep=r"\s+", skiprows=6, header=None)
    else:
        lu_data = pd.read_csv(LUCDATA, sep=r"\s+", skiprows=6, header=None)

    pop_data = pd.read_csv(POPDATA, sep=r"\s+", skiprows=6, header=None)
    emp_data = pd.read_csv(EMPDATA, sep=r"\s+", skiprows=6, header=None)
    trans_data = pd.read_csv(TRANSDATA, sep=r"\s+", skiprows=6, header=None)
    slope_data = pd.read_csv(SLOPEDATA, sep=r"\s+", skiprows=6, header=None)
    bnd_data = pd.read_csv(BNDDATA, sep=r"\s+", skiprows=6, header=None)
    nogo_data = pd.read_csv(NOGODATA, sep=r"\s+", skiprows=6, header=None)
    luo_data = lu_data = pd.read_csv(LUDATA, sep=r"\s+", skiprows=6, header=None)
    lu_row = bnd_data.shape[0]
    lu_col = bnd_data.shape[1]

    with open(LUDATA) as myfile:
        head = [next(myfile) for x in xrange(6)]

    return {'lu': lu_data, 'pop': pop_data, 'emp': emp_data, 'trans': trans_data, 'luo': luo_data,
            'slope': slope_data, 'bnd': bnd_data, 'nogo': nogo_data, 'head': head,
            'row': lu_row, 'col': lu_col}

'''
create mask so that the model only cares about developable cells
'''
def mask_data(lu_data, input_data, ischng, bnd, no_growth, row, col):
    g_mask = np.zeros((row, col))
    g_mask = pd.DataFrame(g_mask)
    if ischng == 0:
        urb_class = [21, 22, 23, 24, 11, 90, 95]  # urbanized or water LU class
    else:
        urb_class = np.array([1, 2, 200, 622, 623, 723])

    u_mask = np.in1d(lu_data, urb_class)  # creating mask of exiting development
    print u_mask.shape
    print row, col
    u_mask = u_mask.reshape((row, col))
    g_mask[(bnd == 1) & (no_growth != 1) & (~u_mask)] = 1
    g_mask = g_mask.values.flatten()
    input_data =  input_data.values.flatten()
    output_data = input_data[g_mask == 1]
    return output_data


def all_neighbors(luo_data):
    aaa

def get_one_neighbor(dist):
    aaa

'''
prepare data into columns
'''
def data_prepare(lu_data, pop_data, emp_data, trans_data, slope, ischng, bnd, nogrowth, row, col):
    lu_col = mask_data(lu_data, lu_data, ischng, bnd, nogrowth, row, col)
    pop_col = mask_data(pop_data, lu_data, ischng, bnd, nogrowth, row, col)
    emp_col = mask_data(emp_data, lu_data, ischng, bnd, nogrowth, row, col)
    trans_col = mask_data(trans_data, lu_data, ischng, bnd, nogrowth, row, col)
    slope_col = mask_data(slope, lu_data, ischng, bnd, nogrowth, row, col)

    if ischg ==0:
        res_class = [21, 22] #creating responses. Change/existing res = 1, other = 0. Same for com
        com_class = [23]
    else:
        res_class = [1021, 1022]  # creating responses. Change/existing res = 1, other = 0. Same for com
        com_class = [1023]

    res_mask = np.in1d(lu_col, res_class)
    com_mask = np.in1d(lu_col, com_class)

    response_col = lu_col
    componse_col = lu_col

    response_col[res_mask] = 1
    response_col[~res_mask] = 0

    componse_col[com_mask] = 1
    componse_col[com_mask] = 0

    return {'pop': pop_col, 'emp': emp_col, 'trans': trans_col, 'slope': slope_col,
            'response': response_col, 'componse': componse_col}

'''
Assemble vectors into Pandas DF
'''
def output_df(pop_col, emp_col, trans_col, slope_col, response_col, componse_col):
    #comnames = np.array(["pop", "emp", "trans", "response_col"])
    #resnames = np.array(["pop", "emp", "trans", "componse_col"])
    #v_size = len(pop_col)
    #colnames = range(v_size)
    res_df = pd.DataFrame({"pop": pop_col, "emp": emp_col, "trans": trans_col, "slope": slope_col,
                           "response": response_col})
    com_df = pd.DataFrame({"pop": pop_col, "emp": emp_col, "trans": trans_col, "slope": slope_col,
                           "componse": componse_col})

    return {'res_df': res_df, 'com_df':com_df}

def main():
    ischg = opt_parser()

    dict = data_loader(ischg)
    [lu_data, pop_data, emp_data, trans_data, luo_data, slope_data, bnd_data, nogo_data, row, col] = \
        [dict.get(k) for k in ('lu', 'pop', 'emp', 'trans', 'luo', 'slope', 'bnd', 'nogo', 'row', 'col')]

    dict = data_prepare(lu_data, pop_data, emp_data, trans_data, slope_data, ischg, bnd_data, nogo_data, row, col)
    [pop_col, emp_col, trans_col, slope_col, response_col, componse_col] = \
        [dict.get(k) for k in ('pop', 'emp', 'trans', 'slope', 'response', 'componse')]

    dict = output_df(pop_col, emp_col, trans_col, slope_col, response_col, componse_col)
    [res_df, com_df] = [dict.get(k) for k in ('res_df','com_df')]

    res_df.to_csv(RESOUT)
    com_df.to_csv(COMOUT)





if __name__ == "__main__":
    main()