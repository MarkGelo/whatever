import argparse
import json
from datetime import datetime
import pandas as pd

# flags
parser = argparse.ArgumentParser(description = "Parameters")
parser.add_argument('--file', default = "", help = "file to parse", required = True)
parser.add_argument('--dateRange', default = "", help = "ONLY FOR PoolEntryDate | (Year/Month/Date) Date range separated by -")
parser.add_argument('--sort', default = "Pool Entry Date", help = 'sort by column. Defaults to "Pool Entry Date". Case insensitive')

FLAGS = parser.parse_args()

def parse(file, dateRange, sort):
    # parse the text file as dictionary
    d = json.load(open(file, 'r'))
    # get first value which is a list of tapes. assuming theres only one key, value in txt file.
    # {Tapes: [...]} or {TapeArchives: [...]} or {TapeInfos: [...]}
    tapes = d[next(iter(d))]
    
    # parse datetime, into actual datetime
    for tape in tapes:
        PoolEntryDate_time = datetime.strptime(tape['PoolEntryDate'][: tape['PoolEntryDate'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        # just ignored the part after the date; 2021-10-14T14:16:11.709000-04:00
        # cuz idk what it is
        tape['PoolEntryDate-Datetime'] = PoolEntryDate_time
        
            
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
            if start <= tape['PoolEntryDate-Datetime'] <= end:
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
        
    tapes.columns = ['Barcode', 'Tape Size', 'Status', 'Pool Id', 'Pool Entry Date', 
                     'PoolEntryDate-Datetime'] # change column names
    
    if sort == 'Pool Entry Date':
        tapes.sort_values(by = ['PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort.lower().title() in tapes.columns: # non dates
        # sorts by parameter and then date
        tapes.sort_values(by = [sort.lower().title(), 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    else:
        print('INVALID SORT PARAMETER')
        return
        
    print('Amazon Resource Name:', resName)
    
    tapes.drop('PoolEntryDate-Datetime', axis = 1, inplace = True)
    
    print(tapes.to_string(index = False))

def parse_all_report(file, dateRange, sort):
    # parse the text file as dictionary
    d = json.load(open(file, 'r'))
    # get first value which is a list of tapes. assuming theres only one key, value in txt file.
    # {Tapes: [...]} or {TapeArchives: [...]} or {TapeInfos: [...]}
    tapes = d[next(iter(d))]
    
    # parse datetime, into actual datetime
    for tape in tapes:
        PoolEntryDate_time = datetime.strptime(tape['PoolEntryDate'][: tape['PoolEntryDate'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        TapeCreatedDate_time = datetime.strptime(tape['TapeCreatedDate'][: tape['TapeCreatedDate'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        # just ignored the part after the date; 2021-10-14T14:16:11.709000-04:00
        # cuz idk what it is
        tape['PoolEntryDate-Datetime'] = PoolEntryDate_time
        tape['TapeCreatedDate-Datetime'] = TapeCreatedDate_time
        
    tapes_ = []
    if dateRange: # only for pool entry date
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
            if start <= tape['PoolEntryDate-Datetime'] <= end:
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
    
    tapes.columns = ['Barcode', 'Tape Created', 'Tape Size', 'Status', 'Tape Used', 'Pool Id', 'Worm', 'Pool Entry Date', 
                     'PoolEntryDate-Datetime', 'TapeCreatedDate-Datetime'] # change column names
    
    if sort == 'Tape Created':
        tapes.sort_values(by = ['TapeCreatedDate-Datetime', 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort == 'Pool Entry Date':
        tapes.sort_values(by = ['PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort.lower().title() in tapes.columns: # non dates
        # sorts by parameter and then date
        tapes.sort_values(by = [sort.lower().title(), 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    else:
        print('INVALID SORT PARAMETER')
        return
        
    print('Amazon Resource Name:', resName)
    
    tapes.drop('PoolEntryDate-Datetime', axis = 1, inplace = True)
    tapes.drop('TapeCreatedDate-Datetime', axis = 1, inplace = True)
    
    # reorder columns
    tapes = tapes[['Barcode', 'Tape Size', 'Tape Used', 'Status', 'Pool Id', 'Worm','Pool Entry Date', 'Tape Created']]
    print(tapes.to_string(index = False))
    
def parse_archived_report(file, dateRange, sort):
    # parse the text file as dictionary
    d = json.load(open(file, 'r'))
    # get first value which is a list of tapes. assuming theres only one key, value in txt file.
    # {Tapes: [...]} or {TapeArchives: [...]} or {TapeInfos: [...]}
    tapes = d[next(iter(d))]
    
    # parse datetime, into actual datetime
    for tape in tapes:
        PoolEntryDate_time = datetime.strptime(tape['PoolEntryDate'][: tape['PoolEntryDate'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        CompletionTime_time =  datetime.strptime(tape['CompletionTime'][: tape['CompletionTime'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        TapeCreatedDate_time = datetime.strptime(tape['TapeCreatedDate'][: tape['TapeCreatedDate'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        # just ignored the part after the date; 2021-10-14T14:16:11.709000-04:00
        # cuz idk what it is
        tape['PoolEntryDate-Datetime'] = PoolEntryDate_time
        tape['CompletionTime-Datetime'] = CompletionTime_time
        tape['TapeCreatedDate-Datetime'] = TapeCreatedDate_time
        
    tapes_ = []
    if dateRange: # only for pool entry date
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
            if start <= tape['PoolEntryDate-Datetime'] <= end:
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
    
    tapes.columns = ['Barcode', 'Tape Created', 'Tape Size', 'Date Archived', 'Status', 'Tape Used', 'Pool Id', 'Worm', 'Pool Entry Date', 
                     'PoolEntryDate-Datetime', 'CompletionTime-Datetime', 'TapeCreatedDate-Datetime'] # change column names
    
    if sort == 'Tape Created':
        tapes.sort_values(by = ['TapeCreatedDate-Datetime', 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort == 'Date Archived':
        tapes.sort_values(by = ['CompletionTime-Datetime', 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort == 'Pool Entry Date':
        tapes.sort_values(by = ['PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort.lower().title() in tapes.columns: # non dates
        # sorts by parameter and then date
        tapes.sort_values(by = [sort.lower().title(), 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    else:
        print('INVALID SORT PARAMETER')
        return
        
    print('Amazon Resource Name:', resName)
    
    tapes.drop('PoolEntryDate-Datetime', axis = 1, inplace = True)
    tapes.drop('CompletionTime-Datetime', axis = 1, inplace = True)
    tapes.drop('TapeCreatedDate-Datetime', axis = 1, inplace = True)
    
    # reorder columns
    tapes = tapes[['Barcode', 'Tape Size', 'Tape Used', 'Status', 'Pool Id', 'Worm', 'Date Archived', 'Pool Entry Date', 'Tape Created']]
    print(tapes.to_string(index = False))
    
if __name__ == '__main__':
    try:
        d = json.load(open(FLAGS.file, 'r'))
        file_type = next(iter(d))
        if file_type == 'Tapes': # all-tape-list-report
            parse_all_report(file = FLAGS.file, dateRange = FLAGS.dateRange, sort = FLAGS.sort)
        elif file_type == 'TapeArchives': # aws-archived-tape-report
            parse_archived_report(file = FLAGS.file, dateRange = FLAGS.dateRange, sort = FLAGS.sort)
        elif file_type == 'TapeInfos': # tape-list
            parse(file = FLAGS.file, dateRange = FLAGS.dateRange, sort = FLAGS.sort)
    except Exception as e:
        print(e)