import numpy as np
import math

class revert_network:
    def __init__(self, data):
        """Initialize the revert network"""
        self.data = data
        self.network = []
        self.nodes = set()

    def find_reverter_events(self):
        """find the reverter events"""
        for i in range(len(self.data)):
            if self.data[i][2] == 1:
                yield i

    def find_restored_version(self, index):
        """find the originally edited version
          with the same restored_version"""
        restored_version = self.data[index][3]
        for j in range(index + 1, len(self.data)):
            if self.data[j][3] == restored_version:
                return j
        return None

    def find_reverted(self, reverter_index, restored_index):
        """find the reverted edit, which is the immediate edit
        after the originally edited version"""
        if restored_index and restored_index > 0:
            reverter = self.data[reverter_index][4]
            reverted = self.data[restored_index - 1][4]
            if reverter != reverted:
                return reverted
        return None

    def create_network(self):
        """Store reverter-reverted pairs in self.network
          and store all nodes in self.nodes"""
        for reverter_index in self.find_reverter_events():
            restored_index = self.find_restored_version(reverter_index)
            reverted = self.find_reverted(reverter_index, restored_index)
            if reverted:
                reverter = self.data[reverter_index][4]
                dt = self.data[reverter_index][1]
                
                self.network.append((reverter, reverted, dt))
                self.nodes.add(reverter)
                self.nodes.add(reverted)

class seniority_calculator:
    def __init__(self, network, data):
        self.network = network
        # Make sure the data is sorted by date
        self.data = np.array(data, dtype='object')
        # Sort the data by date
        self.data = self.data[np.argsort(self.data[:, 1])]
        self.edit_history = self.build_edit_history()

    def build_edit_history(self):
        """Build a dictionary of edit history for each editor."""
        edit_history = {}
        for record in self.data:
            editor, time = record[4], record[1]
            if editor not in edit_history:
                edit_history[editor] = []
            edit_history[editor].append(time)

        return edit_history

    def calculate_seniority(self, editor, cutoff_time):
        """Calculate the seniority of an editor before the revert."""
        if editor not in self.edit_history:
            return 0

        edits = sum(time < cutoff_time for time in self.edit_history[editor])
        return math.log10(edits) if edits > 0 else 0

    def add_seniority_info(self):
        """Add seniority information to each edge in the network."""
        updated_network = []
        for edge in self.network.network:
            reverter, reverted, dt = edge
            reverter_seniority = self.calculate_seniority(reverter, dt)
            reverted_seniority = self.calculate_seniority(reverted, dt)
            seniority_difference = reverter_seniority - reverted_seniority
            updated_network.append(edge + (reverter_seniority, reverted_seniority, seniority_difference))
        self.network.network = updated_network
        
    def seniority_difference(self, edge):
        """Calculate the seniority difference for a given edge."""
        reverter, reverted, dt, reverter_seniority, reverted_seniority = edge
        return abs(reverter_seniority - reverted_seniority)   
    
def calculate_seniority_diffs(network_with_seniority, ab_ba_sequences):
    """Calculate seniority differences for AB-BA sequences and other reverts."""
    # Calculate seniority differences for AB-BA sequences
    ab_ba_seniority_diffs = [
        network_with_seniority.seniority_difference(ab_edge[:5])
        for ab_edge, _ in ab_ba_sequences
    ]
    # Calculate seniority differences for other reverts
    other_reverts_seniority_diffs = [
        network_with_seniority.seniority_difference(edge[:5])
        for edge in network_with_seniority.network.network
        if edge not in [ab_edge for ab_edge, _ in ab_ba_sequences]
    ]
    return ab_ba_seniority_diffs, other_reverts_seniority_diffs

