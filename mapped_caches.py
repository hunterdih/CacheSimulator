import pandas as pd
import numpy as np
from collections import deque


class MappedCache:
    def __init__(self, associativity=1, cache_size=8, block_size=32, replacement_policy='lru', cache_level='l1'):
        self.cache_size = cache_size # Save the cache size
        self.block_size = block_size # Save the block size
        self.associativity = associativity # Save the associativity
        # Create the cache (represented by a DataFrame)
        self.cache = pd.DataFrame(index=range(int((self.cache_size * 1024) / self.block_size)), columns=range(1))
        # Only need to save the tag, index is equal to the row in the cache
        self.cache.columns = ['Tag']
        # Save the number of available sets
        self.number_cache_sets = len(bin(int((self.cache_size * 1024) / (self.block_size * self.associativity)))) - 2
        # Implement a deque, used for a LRU replacement policy
        deque_values = list(range(self.associativity))
        num_deques = int((self.cache_size * 1024) / (self.block_size * self.associativity))
        self.deque_list = []
        # Populate the deque with initial LRU values
        for i in range(num_deques):
            self.deque_list.append(deque(deque_values, maxlen=self.associativity))
        # Create data metrics
        self.miss_total = 0
        self.hit_total = 0
        self.instr_count = 0
        self.replacement_policy = replacement_policy
        self.cache_level = cache_level

    def print_metrics(self):
        print(f'\nResults for {self.cache_level} data cache...')
        print(f'Cache Metrics:\n{self.associativity}-Way Mapped Cache, Cache Size: {self.cache_size}, Block Size {self.block_size}')
        print(f'Hit Ratio = {self.hit_total / self.instr_count}')
        print(f'Miss Ratio = {self.miss_total / self.instr_count}')

        return self.hit_total/self.instr_count, self.miss_total/self.instr_count

    def process_address(self, input_address):
        self.instr_count += 1  # Update the instruction count
        block_size = len(bin(self.block_size)) - 2  # -2 for byte addressing

        # Determine if read or write, if write assume write-through

        address = '{:032b}'.format((int(input_address, 16)))  # Address of interest
        address_block_removed = address[:-block_size]  # Address not including the block
        tag = address_block_removed[:-self.number_cache_sets]  # Tag based on set associativity
        index = int(address_block_removed[-(self.number_cache_sets - 1):], 2) * self.associativity
        dqi = int(address_block_removed[-(self.number_cache_sets - 1):], 2)

        # Retrieve Set
        for i in range(self.associativity):
            #interest_row = self.cache.iloc[index+i]['Tag']
            if self.cache.iloc[index+i]['Tag'] == tag: # See if tag matches
                self.hit_total += 1 # Record a hit

                # Remove index from deque
                self.deque_list[dqi].remove(i)
                # Move to first element in deque
                self.deque_list[dqi].appendleft(i)
                return 'hit' # Break out of function, return hit

        # If you have reached this point, there was a miss
        if self.replacement_policy == 'lru':
            self.miss_total += 1

            # Find lru
            i = self.deque_list[dqi][-1]
            self.deque_list[dqi].remove(i)
            self.deque_list[dqi].appendleft(i)

            self.cache['Tag'][index+i] = tag
            return 'miss'



