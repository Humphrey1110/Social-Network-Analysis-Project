from datetime import datetime
import matplotlib.pyplot as plt

def get_data(fname):
    """
    Read data from a file and return lists of records.
    Each record consists of the article title, 
    datetime of edit, revision number, version number, and user.
    """
    data = []
    with open(fname, 'r') as f:
        # Skip the header line
        f.readline()  
        for edit in f.readlines():
            title, dt_str, rev, version, user = edit.strip().split('\t')
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            # Convert datetime string to datetime object
            data.append([title.strip(), dt, int(rev), int(version), user])
    return data

def match_sequences(network):
    """
    Find AB-BA event sequences in the network.
    AB-BA sequence occurs when A reverts B 
    and then B reverts A within 24 hours.
    """
    ab_ba_sequences = []
    for ab_edge in network.network:
        reverter_A, reverted_B, dt_A = ab_edge[:3]  
        for ba_edge in network.network:
            reverter_B, reverted_A, dt_B = ba_edge[:3]  
            # Ensure BA event occurs after AB and within 24 hours
            if (reverter_B == reverted_B and reverted_A == reverter_A and 
                dt_B > dt_A and 
                (dt_B - dt_A).total_seconds() <= 24 * 3600):
                ab_ba_sequences.append((ab_edge, ba_edge))
                # Consider only the first matching BA event
                break  
    return ab_ba_sequences

def plot_seniority_diff_histogram(ab_ba_seniority_diffs, other_reverts_seniority_diffs):
    """
    Plot histograms comparing seniority differences for AB-BA sequences and other reverts.
    """
    plt.figure(figsize=(12, 6))
    plt.hist(ab_ba_seniority_diffs, 
             bins=30, 
             alpha=0.7, 
             color='darkblue', 
             label='AB-BA Seniority Differences',
             # normalize the figure to make better comparison
             density=True)
    plt.hist(other_reverts_seniority_diffs, 
             bins=30, 
             alpha=0.5, 
             color='lightblue', 
             label='Other Reverts Seniority Differences',
             density=True)
    plt.xlabel('Seniority Difference')
    plt.ylabel('Frequency')
    plt.title('Histogram of Seniority Differences')
    plt.legend()
    plt.show()
