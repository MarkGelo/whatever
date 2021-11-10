import argparse
import json
from datetime import datetime
import pandas as pd

# flags
parser = argparse.ArgumentParser(description = "Parameters")
parser.add_argument('--file', default = "", help = "file to parse", required = True)
parser.add_argument('--dateRange', default = "", help = " (Year/Month/Date) Date range separated by -")
parser.add_argument('--sort', default = "date", help = "sort by location/status/tapesize/barcode. Defaults to date")

FLAGS = parser.parse_args()

def parse(file, dateRange, sort):
    # parse the text file as dictionary
    d = json.load(open(file, 'r'))
    tapes = d['TapeInfos']
    
    # parse datetime, into actual datetime
    for tape in tapes:
        tape_time = datetime.strptime(tape['PoolEntryDate'][: tape['PoolEntryDate'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        # just ignored the part after the date; 2021-10-14T14:16:11.709000-04:00
        # cuz idk what it is
        tape['Datetime'] = tape_time
        
            
    tapes_ = []
    if dateRange:
        # parse dateRange
        try:
            start, end = dateRange.split('-')
            start = datetime.strptime(start, '%Y/%m/%d')
            end = datetime.strptime(end, '%Y/%m/%d')
        except Exception as e:
            print('Invalid Date Range format. Example: 2021/08/01-2021/08/26')
            return
        
        # eliminate tapes not in that date range
        for tape in tapes:
            if start <= tape['Datetime'] <= end:
                #print(tape_time)
                tapes_.append(tape)
    
        tapes = tapes_
        
        if not tapes: # empty, nothing within that range
            return
    
    # where to get resource name
    temp = tapes[0]['TapeARN']
    resName = temp[temp.find('arn:aws:') + 8:temp.find(':tape')] if ':tape' in temp else temp[temp.find('arn:aws:') + 8:temp.find(':gateway')]
    
    tapes = pd.DataFrame(tapes)
    if 'GatewayARN' in tapes.columns:
        tapes.drop('GatewayARN', axis = 1, inplace = True)
    if 'TapeARN' in tapes.columns:
        tapes.drop('TapeARN', axis = 1, inplace = True)
        
    tapes.columns = ['Barcode', 'Tapesize', 'Status', 'Location', 'Date', 'DateTime'] # change column names
    
    if sort.lower() in ['barcode', 'tapesize', 'status', 'location', 'date']:
        # sorts by parameter and then date
        tapes.sort_values(by = [sort.lower().capitalize(), 'DateTime'], ascending = True, inplace = True)
    else:
        print('INVALID SORT PARAMETER')
        return
        
    print('Amazon Resource Name:', resName)
    
    tapes.drop('DateTime', axis = 1, inplace = True)
    print(tapes.to_string(index = False))

if __name__ == '__main__':
    try:
        parse(file = FLAGS.file, dateRange = FLAGS.dateRange, sort = FLAGS.sort)
    except Exception as e:
        print(e)