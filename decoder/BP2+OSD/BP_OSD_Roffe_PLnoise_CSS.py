# Import dependencies

import numpy as np
import random
import ldpc
from ldpc.codes import hamming_code
from bposd.css import css_code
from ldpc.codes import rep_code
from bposd.hgp import hgp
from bposd.css_decode_sim import css_decode_sim
from ldpc.codes import rep_code
# from ldpc import bposd_decoder
from ldpc import BpOsdDecoder
import matplotlib.pyplot as plt

# Print array without double square brackets
def print_ndarray(array):
    formatted_rows = ["[" + " ".join(map(str, row)) + "]" for row in array]
    print("\n".join(formatted_rows))


def format_matrix(matrix):
    """
    Properly formats and prints a matrix of matrices (block matrix).
    """
    # Stack each row of blocks horizontally
    full_rows = [np.hstack(row) for row in matrix]
    
    # Stack all full rows vertically
    full_matrix = np.vstack(full_rows)
    
    # Print the full matrix
    print(full_matrix)


def binary_rank(A):
    """
    Compute the rank of a binary matrix (over GF(2)).

    Args:
        A (np.ndarray): Binary matrix (elements 0 or 1)

    Returns:
        int: Rank of A over GF(2)
    """
    A = A.copy() % 2  # ensure we work mod 2
    rows, cols = A.shape
    rank = 0
    col = 0

    for r in range(rows):
        # Find a pivot in or below row r
        while col < cols and not np.any(A[r:, col]):
            col += 1
        if col == cols:
            break

        # Find the first row with a 1 in this column and swap
        pivot_row = r + np.argmax(A[r:, col])
        A[[r, pivot_row]] = A[[pivot_row, r]]

        # Eliminate 1s below the pivot (mod 2)
        for i in range(r + 1, rows):
            if A[i, col] == 1:
                A[i] = (A[i] + A[r]) % 2

        rank += 1
        col += 1

    return rank


# Load PCMs
###################################################################################################################################

# High-girth Dyadics
# H_X = np.loadtxt("/Users/baldellaux/Desktop/VS_python/dyadics/high_girth_dyadics/QD[[128,36,8]]_H_X.csv", delimiter="," , dtype=int) 
# H_Z = np.loadtxt("/Users/baldellaux/Desktop/VS_python/dyadics/high_girth_dyadics/QD[[128,36,8]]_H_Z.csv", delimiter="," , dtype=int)
# M_X = np.loadtxt("/Users/baldellaux/Desktop/VS_python/dyadics/high_girth_dyadics/QD[[128,36,8]]_M_X.csv", delimiter="," , dtype=int) 
# M_Z = np.loadtxt("/Users/baldellaux/Desktop/VS_python/dyadics/high_girth_dyadics/QD[[128,36,8]]_M_Z.csv", delimiter="," , dtype=int)

H_X = np.loadtxt("/Users/baldellaux/Desktop/VS_python/dyadics/high_girth_dyadics/QD[[64,18,8]]_H_X.csv", delimiter="," , dtype=int) 
H_Z = np.loadtxt("/Users/baldellaux/Desktop/VS_python/dyadics/high_girth_dyadics/QD[[64,18,8]]_H_Z.csv", delimiter="," , dtype=int)
M_X = np.loadtxt("/Users/baldellaux/Desktop/VS_python/dyadics/high_girth_dyadics/QD[[64,18,8]]_M_X.csv", delimiter="," , dtype=int) 
M_Z = np.loadtxt("/Users/baldellaux/Desktop/VS_python/dyadics/high_girth_dyadics/QD[[64,18,8]]_M_Z.csv", delimiter="," , dtype=int)

###################################################################################################################################


m_X , n = H_X.shape
print(H_X.shape)
m_Z , n = H_Z.shape
print(H_Z.shape)
rank_X = binary_rank(H_X)
rank_Z = binary_rank(H_Z)

# d_min = 8 # it is able to correct weight 3 errors
# corr_cap = 3 # error-correction capability 

### Creating a valid CSS code.
QLDPC = css_code(
    hx=H_X, hz=H_Z
) 
# print_ndarray(QLDPC.hx)

print("Lx Logical")
print(QLDPC.lx)
print("Lz Logical")
print(QLDPC.lz)

QLDPC.test()


# Constructing the PL PCM
H_tilde = np.block([
    [H_X, np.eye((m_X), dtype = int)],
    [np.zeros(((m_X - rank_X), n), dtype = int), M_X]
])

# Probabilities
# prob = [0.1, 0.09, 0.08, 0.07, 0.06, 0.050, 0.045, 0.040, 0.035, 0.030, 0.025, 0.020, 0.015, 0.010, 0.009, 0.008, 0.007, 0.006, 0.005, 0.004, 0.003, 0.002, 0.001]
prob = [0.5, 0.4, 0.3, 0.2, 0.1, 0.09, 0.07, 0.06, 0.050, 0.040, 0.030, 0.020, 0.010, 0.009, 0.008, 0.007, 0.006, 0.005, 0.004, 0.003, 0.002, 0.001] 
# prob = [0.006, 0.005, 0.004, 0.003, 0.002, 0.001] # if so, then num_dec_max = 100 in num_dec_max = 50.
l_axis = len(prob)

# Start decoding
print(f"Start decoding...\n")
x_axis = []
y_axis = []

# Start of the simulator
for p in prob:
    wrong_frames = 0  
    tx_frames = 0 
    num_dec_max = 100
    p_cross = (2*p)/3 # crossover probability of the associated depolarizing channel
    epsilon = 0 # 10**(-3) # syndrome read-out errors probability (PL noise)
    th = 10**9 # maximum threshold for transmitted frames

    # Class of BP decoder.
    bp_osd = BpOsdDecoder(
            H_tilde,
            error_rate = 0.001,
            channel_probs=[
                None
            ],  # assign error_rate to each qubit. This will override "error_rate" input variable
            max_iter = 100, 
            bp_method = "ms",
            ms_scaling_factor = 0.05, # 0.080, # since I use min-sum
            osd_method = 'cs', #set to OSD_0 for fast solve
            osd_order = 0
        )

    while (tx_frames < th) and (wrong_frames <  num_dec_max):
        # Data qubit error vector
        e = np.zeros(n).astype(int)
        # Build the error vector e
        e = (np.random.random(n) < p_cross).astype(np.uint8)
        # weight = np.count_nonzero(e)
        # support = np.nonzero(e)[0]
        
        # Syndrome read-out error vector
        e_s = np.zeros(m_X).astype(int)
        # Build the error vector e_s
        e_s = (np.random.random(m_X) < epsilon).astype(np.uint8)
        
        # Build e_tilde = [e | e_s]
        e_tilde = np.hstack((e, e_s))

        # Compute the syndrome
        s_tilde = (H_tilde @ np.transpose(e_tilde)) %2

        # syndrome-based BP decoding: decoded is the estimated error vector by the decoder
        decoded = bp_osd.decode(s_tilde)
        decoded_e = decoded[:n] # decoded_e is a length n binary vector
        decoded_es = decoded[n:] # decoded_e_tilde is a length m binary vector
        
        # Compute the residual error only in the "e" error part
        residual_error = (decoded_e + e) % 2
        # Check if the residual error is a stabilizer 
        commute = QLDPC.lx@residual_error % 2   
        logical_failure = (commute).any()  # logical_failure is True if AT LEAST one of its entries is distinct from 0, i.e., they don't commute.
        
        # Meta-check failure on syndrome bits?
        residual_error_s = (decoded_es + e_s) % 2
        meta_failure = ((M_X @ residual_error_s) % 2).any()
        
        if logical_failure or meta_failure:
            wrong_frames += 1
            # print(f"\nuncorrected error of wt(e) =", weight)
            # print(f"support(e) =", support)
            print(f"wrong frames = {wrong_frames}, tx frames = {tx_frames}, LER = {wrong_frames/(tx_frames + 1)}, at p = {p}, epsilon = {epsilon} \n")
        # else:
            # if weight > corr_cap:
                # print(f"corrected error of wt(e) =", weight)

        # Compute LER
        tx_frames += 1
        LER = wrong_frames/tx_frames
        # print(f"LER: {LER}, with p={p} and FT = {tx_frames} \n")

    # Build the two axes vectors
    x_axis.append(p)
    y_axis.append(LER)

    # Print axes
    print(f"probabilities: {x_axis} \n")
    print(f"LER: {y_axis} \n")
    print(f"------------------------------------------")

# Print axes
print(f"probabilities: {x_axis} \n")
print(f"LER: {y_axis} \n")

# Print axes
print(f"probabilities: {x_axis} \n")
print(f"LER: {y_axis} \n")

def print_dfr_pairs_multiline(prob, y_axis):
    # if not (len(prob) == len(y_axis)):
        # raise ValueError("Each list must have the same length.")

    print("LER =")
    for p, cer in zip(prob, y_axis):
        print(f"({p}, {cer})")

print_dfr_pairs_multiline(prob, y_axis)