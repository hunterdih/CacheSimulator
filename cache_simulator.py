import column_associative_cache
import mapped_caches
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    l1_hit_rate = []
    l1_miss_rate = []
    l2_miss_rate = []
    l2_hit_rate = []
    test_format_list = []
    l1_cache_assoc = [1, 'CA', 'CALRU']
    l1_cache_sizes = [2, 4]
    l2_cache_assoc = [2, 4]
    l2_cache_sizes = [8]
    l1_block_size = 32
    l2_block_size = 64

    #address_stream_path = r'D:\Classes\ComputerArchitecture\FinalProject\linpack_address_trace_use.out'
    address_stream_path = r'C:\Users\David Hunter\Desktop\Traces\sodoku_trace_use.out'
    dataset = pd.read_csv(address_stream_path, delimiter=' ')
    dataset = dataset[dataset.columns[0:2]]
    dataset.columns = ['type', 'element']
    dataset = dataset[dataset['type'].isin([0, 1])].reset_index(inplace=False, drop=True)

    for l1_assoc in l1_cache_assoc:
        for l2_assoc in l2_cache_assoc:
            for l1_size in l1_cache_sizes:
                for l2_size in l2_cache_sizes:

                    if l1_assoc == 'CA':
                        cachel1 = column_associative_cache.ColumnCache(cache_size=l1_size, block_size=l1_block_size, cache_level='l1')
                    elif l1_assoc == 'CALRU':
                        cachel1 = column_associative_cache.LRUColumnCache2(cache_size=l1_size, block_size=l1_block_size, cache_level='l1')
                    else:
                        cachel1 = mapped_caches.MappedCache(associativity=l1_assoc, cache_size=l1_size, block_size=l1_block_size, cache_level='l1')

                    if l2_assoc == 'CA':
                        cachel2 = column_associative_cache.ColumnCache(cache_size=l2_size, block_size=l2_block_size, cache_level='l2')
                    elif l2_assoc == 'CALRU':
                        cachel2 = column_associative_cache.LRUColumnCache2(cache_size=l2_size, block_size=l2_block_size, cache_level='l2')
                    else:
                        cachel2 = mapped_caches.MappedCache(associativity=l2_assoc, cache_size=l2_size, block_size=l2_block_size, cache_level='l2')

                    print(f'Running Test: {l1_assoc=} {l1_size=}, {l2_assoc=} {l2_size=}...')
                    address_count = 0
                    for element in dataset.values:
                        if address_count % 10000 == 0:
                            print(f'{address_count=}')
                        address_count += 1
                        result = cachel1.process_address(input_address=element[1])

                        if result == 'miss':  # Check L2, if not there update
                            cachel2.process_address(input_address=element[1])

                    l1_hit, l1_miss = cachel1.print_metrics()
                    l2_hit, l2_miss = cachel2.print_metrics()
                    l1_hit_rate.append(l1_hit)
                    l1_miss_rate.append(l1_miss)
                    l2_hit_rate.append(l2_hit)
                    l2_miss_rate.append(l2_miss)
                    test_format_list.append('L1: ' + str(l1_assoc) + '-assoc ' + str(l1_size) + 'KB ' + 'L2: ' + str(l2_assoc) + '-assoc ' + str(l2_size) + 'KB')
    ind = np.arange(len(test_format_list))
    width = 0.35
    fig0 = plt.figure(0, figsize=(12, 9))
    plt.tight_layout
    p1 = plt.bar(ind, l1_hit_rate, width)
    p2 = plt.bar(ind, l1_miss_rate, width, bottom=l1_hit_rate, )
    plt.title('L1 Cache')
    plt.ylabel('Rate')
    plt.xlabel(f'Test, Hit Rates {l1_hit_rate}')
    plt.yticks(np.arange(0, 1.01, 0.05))
    plt.xticks(ind, test_format_list)
    plt.legend((p1[0], p2[0]), ('Hit Rate', 'Miss Rate'))

    fig1 = plt.figure(1, figsize=(12, 9))
    plt.tight_layout
    p1 = plt.bar(ind, l2_hit_rate, width)
    p2 = plt.bar(ind, l2_miss_rate, width, bottom=l2_hit_rate)
    plt.title('L2 Cache')
    plt.ylabel('Rate')
    plt.xlabel(f'Test, Hit Rates {l2_hit_rate}')
    plt.yticks(np.arange(0, 1.01, 0.05))
    plt.xticks(ind, test_format_list)
    plt.legend((p1[0], p2[0]), ('Hit Rate', 'Miss Rate'))

    plt.show()
