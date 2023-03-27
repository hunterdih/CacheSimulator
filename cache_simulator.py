import column_associative_cache
import mapped_caches
import pandas as pd
import numpy as np

if __name__ == '__main__':

    address_stream_path = r'C:\Users\David Hunter\Desktop\tracefile\trace'
    dataset = pd.read_csv(address_stream_path, delimiter=' ')
    dataset.columns = ['type', 'element']

    dataset = dataset[dataset['type'].isin([0, 1])].reset_index(inplace=False, drop=True)

    cachel1 = mapped_caches.MappedCache(associativity=1, cache_size=8, block_size=32, cache_level='l1')
    cachel2 = mapped_caches.MappedCache(associativity=2, cache_size=16, block_size=64, cache_level='l2')

    address_count = 0
    for element in dataset.values:
        address_count += 1
        if address_count % 10000 == 0:
            print(f'Processed {address_count} Instructions...')
        result = cachel1.process_address(type=element[0], input_address=element[1])

        if result == 'miss':  # Check L2, if not there update
            cachel2.process_address(type=element[0], input_address=element[1])

    cachel1.print_metrics()
    cachel2.print_metrics()
