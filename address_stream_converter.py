import numpy as np
import pandas as pd
import csv

if __name__ == '__main__':
    address_path = r'C:\Users\dihdd\OneDrive\Desktop'
    colnames = ['Instruction Address', 'Write/Read', 'Data Address']
    address_stream = pd.read_csv(address_path + r'\linpack_address_trace.out', names=colnames, delimiter=' ')
    print(f'Address Stream Loaded...')
    address_stream = address_stream.drop('Instruction Address', axis=1)
    print(f'Instruction Addresses Dropped...')
    address_stream[['0x', 'Data Address']] = address_stream['Data Address'].str.split('x', expand=True)
    address_stream = address_stream.drop('0x', axis=1)
    print(f'0x Dropped From Hex...')
    address_stream['Write/Read'] = address_stream['Write/Read'].replace(['R', 'W'], ['0', '1'])
    print(f'R/W Replaced with 0/1...')
    address_stream = address_stream['Write/Read'] + ' ' + address_stream['Data Address'] + '  \n'

    with open(address_path + r'\linpack_address_trace_use.out', 'a') as f:
        for i in address_stream:
            f.write(i)
    print(f'File Saved, Done...')
