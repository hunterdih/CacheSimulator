import pandas as pd
import numpy as np
from collections import deque


class ColumnCache:
    def __init__(self, cache_size=8, block_size=32, cache_level='l1'):
        '''
        :param cache_size: Size of the cachel1, passed in KiloBytes
        :param block_size: Block size of each cachel1 index, passed in Bytes
        :param cache_level: Level of the cachel1, Ex: l1, l2, l3... Used for final data outputs
        '''
        self.cache_size = cache_size
        self.block_size = block_size

        # Program is intended to only model an Data cachel1, so other addresses can be ignored
        self.column_cache = pd.DataFrame(index=range(int((self.cache_size * 1024) / self.block_size)), columns=range(2))
        self.column_cache.columns = ['Tag', 'Rehash']
        self.number_cache_indexes = len(bin(int((self.cache_size * 1024) / self.block_size))) - 2
        self.column_cache['Rehash'] = 1
        self.miss_total = 0
        self.hit_total = 0
        self.instr_count = 0
        self.cache_level = cache_level

    def print_metrics(self):
        print(f'Results for {self.cache_level} data cache...')
        print(f'Cache Metrics:\nColumn Associative Cache, Cache Size: {self.cache_size}, Block Size {self.block_size}')
        print(f'Hit Ratio = {self.hit_total / self.instr_count}')
        print(f'Miss Ratio = {self.miss_total / self.instr_count}')
        print(f'\n')

        return self.hit_total / self.instr_count, self.miss_total / self.instr_count

    def process_address(self, type, input_address):
        self.instr_count += 1  # Update the instruction count
        block_size = len(bin(self.block_size)) - 2  # -2 for byte addressing

        # Determine if read or write, if write assume write-through

        address = '{:032b}'.format((int(input_address, 16)))  # Address of interest
        address_block_removed = address[:-block_size]  # Address not including the block

        tag = address_block_removed[:-self.number_cache_indexes]  # Tag for cache to memory mapping
        index0 = int(address_block_removed[-(self.number_cache_indexes - 1):], 2)  # Index for state 0

        if not tag == self.column_cache['Tag'][index0]:  # MISS
            if self.column_cache['Rehash'][index0] == 1:
                self.miss_total += 1
                # Update stored element
                self.column_cache['Tag'][index0] = tag
                # Update Rehash bit
                self.column_cache['Rehash'][index0] = 0
                return 'miss'
            else:

                # Perform bit flip of first bit in index
                index1 = bin(index0)
                test = index1[2:]
                if index1[2] == '1':
                    index1 = index1[:2] + '0' + index1[2:]
                else:
                    index1 = index1[:2] + '1' + index1[3:]
                index1 = int(index1, 2)

                # Check if element is stored in the offset portion of the cachel1
                if not tag == self.column_cache['Tag'][index1]:  # MISS

                    self.miss_total += 1
                    # Store element in cachel1
                    self.column_cache['Tag'][index1] = tag
                    self.column_cache['Rehash'][index1] = 0

                    # Perform swap
                    # Load 1 to temp cachel1
                    temp_cache_tag = self.column_cache['Tag'][index0]
                    temp_cache_rehash = self.column_cache['Rehash'][index0]

                    # Swap 2 into 1
                    self.column_cache['Tag'][index0] = self.column_cache['Tag'][index1]
                    self.column_cache['Rehash'][index0] = self.column_cache['Rehash'][index1]

                    # Swap temp (1) into 2
                    self.column_cache['Tag'][index1] = temp_cache_tag
                    self.column_cache['Rehash'][index1] = temp_cache_rehash

                    return 'miss'

                # Condition for a delayed hit
                else:  # HIT

                    self.hit_total += 1
                    # Perform swap
                    # Load to temp cachel1
                    temp_cache_tag = self.column_cache['Tag'][index0]
                    temp_cache_rehash = self.column_cache['Rehash'][index0]

                    # Swap 2 into 1
                    self.column_cache['Tag'][index0] = self.column_cache['Tag'][index1]
                    self.column_cache['Rehash'][index0] = self.column_cache['Rehash'][index1]

                    # Swap temp (1) into 2
                    self.column_cache['Tag'][index1] = temp_cache_tag
                    self.column_cache['Rehash'][index1] = temp_cache_rehash
                    return 'hit'
        # Condition for hit on the first check
        else:  # HIT
            self.hit_total += 1
            return 'hit'


class LRUColumnCache2:
    def __init__(self, cache_size=8, block_size=32, cache_level='l1'):
        '''
        This is a pseudo associative caching algorithm that eliminates the rehash bits, and improves temporal locality
        :param cache_size: Size of the cachel1, passed in KiloBytes
        :param block_size: Block size of each cachel1 index, passed in Bytes
        :param cache_level: Level of the cachel1, Ex: l1, l2, l3... Used for final data outputs
        '''
        self.cache_size = cache_size
        self.block_size = block_size

        # Program is intended to only model an Data cachel1, so other addresses can be ignored
        self.column_cache = pd.DataFrame(index=range(int((self.cache_size * 1024) / self.block_size)), columns=range(2))
        self.column_cache.columns = ['Tag', 'Rehash']
        self.number_cache_indexes = len(bin(int((self.cache_size * 1024) / self.block_size))) - 2
        deque_values = 0
        num_deques = int((self.cache_size * 1024) / (self.block_size * 2))
        self.lru_bit_cache = []
        for i in range(num_deques):
            self.lru_bit_cache.append(deque_values)
        self.miss_total = 0
        self.hit_total = 0
        self.instr_count = 0
        self.cache_level = cache_level

    def print_metrics(self):
        print(f'Results for {self.cache_level} data cache...')
        print(f'Cache Metrics:\nColumn Associative Cache, Cache Size: {self.cache_size}, Block Size {self.block_size}')
        print(f'Hit Ratio = {self.hit_total / self.instr_count}')
        print(f'Miss Ratio = {self.miss_total / self.instr_count}')
        print(f'\n')

        return self.hit_total / self.instr_count, self.miss_total / self.instr_count

    def process_address(self, input_address):
        self.instr_count += 1  # Update the instruction count
        block_size = len(bin(self.block_size)) - 2  # -2 for byte addressing

        # Determine if read or write, if write assume write-through

        address = '{:032b}'.format((int(input_address, 16)))  # Address of interest
        address_block_removed = address[:-block_size]  # Address not including the block

        tag = address_block_removed[:-self.number_cache_indexes]  # Tag for cache to memory mapping
        lru_cache_index_bin = address_block_removed[-(self.number_cache_indexes - 2):]
        lru_cache_index = int(lru_cache_index_bin, 2) - 1 # 1 is subtracted for 0 indexing

        # Get mru bit from lru cache and use it to calculate the mru_index_int
        mru_index_bin = address_block_removed[-(self.number_cache_indexes - 1):]
        mru_index_bin = str(self.lru_bit_cache[lru_cache_index]) + mru_index_bin[1:]
        mru_index_int = int(mru_index_bin, 2)

        lru_index_bin = address_block_removed[-(self.number_cache_indexes - 1):]


        if self.lru_bit_cache[lru_cache_index] == 0:
            lru_index_bin = str(1) + lru_index_bin[1:]
        else:
            lru_index_bin = str(0) + lru_index_bin[1:]
        lru_index_int = int(lru_index_bin, 2)

        if mru_index_int == -1:
            print("DEBUGGING")
            print(f'MRU_INDEX: {mru_index_int}, LRU_INDEX: {lru_index_int}')

        if self.column_cache['Tag'][mru_index_int] == tag:  # Condition for a hit
            self.hit_total += 1
            self.lru_bit_cache[lru_cache_index] = int(str(mru_index_bin)[0])
            return 'hit'

        elif self.column_cache['Tag'][lru_index_int] == tag:  # Missed on first go, check the LRU location for a hit
            self.hit_total += 1
            self.lru_bit_cache[lru_cache_index] = int(str(lru_index_bin)[0])
            return 'hit'

        else: # Miss detected, overwrite the data in the lru index and update the lru_cache
            self.miss_total += 1
            self.column_cache['Tag'][lru_index_int] = tag

            self.lru_bit_cache[lru_cache_index] = int(str(lru_index_bin)[0])
            return 'miss'
