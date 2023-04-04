import pandas as pd

if __name__ == '__main__':
    address_path = r'C:\Users\David Hunter\Desktop\Traces'
    colnames = ['Instruction Address', 'Write/Read', 'Data Address']

    # Read the input address stream into the python script
    address_stream = pd.read_csv(address_path + r'\sodoku_trace.out', names=colnames, delimiter=' ')
    print(f'Address Stream Loaded, number of addresses to process: {address_stream.values.shape[0]}')

    # Drop the instruction address field
    address_stream = address_stream.drop('Instruction Address', axis=1)
    print(f'Instruction Addresses Dropped...')

    # Remove the leading 0x from the data address
    address_stream[['0x', 'Data Address']] = address_stream['Data Address'].str.split('x', expand=True)
    address_stream = address_stream.drop('0x', axis=1)
    print(f'0x Dropped From Hex...')

    # Replace each R and W with 0 or 1
    address_stream['Write/Read'] = address_stream['Write/Read'].replace(['R', 'W'], ['0', '1'])
    print(f'R/W Replaced with 0/1...')

    # Combine each DataFrame column into a single Series
    address_stream = address_stream['Write/Read'] + ' ' + address_stream['Data Address'] + '  \n'

    with open(address_path + r'\sodoku_trace_use.out', 'a') as f:
        '''
        Loop through the address stream and write to an output file 
        (Using a for loop proved to be faster than using the built in function)
        '''
        for i in address_stream:
            f.write(i)
    print(f'File Saved, Done...')


