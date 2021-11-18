import argparse
import json
from datetime import datetime
import pandas as pd
from tabulate import tabulate

# flags
parser = argparse.ArgumentParser(description = "Parameters")
parser.add_argument('--file', default = "", help = "file to parse", required = True)
parser.add_argument('--dateRange', default = "", help = '''ONLY FOR date columns | "Column: (Year/Month/Date)" Date range separated by "-".
                    Example: "Date Archived: 2021/08/19-2021/10/26" Case sensitive
                    ''')
parser.add_argument('--sort', default = "Pool Entry Date", help = '''sort by column. Defaults to "Pool Entry Date". Case insensitive.
                    Example: "Tape Used"
                    ''')
parser.add_argument('--search', default = "", help = '''require certain value for a column. Can have multiple requirements separated by a comma.
                    Example: "Pool ID: GLACIER" or "Pool ID: GLACIER, Status: ARCHIVED" Case sensitive and space sensitive for column name
                    ''')

FLAGS = parser.parse_args()

DATES = ['Pool Entry Date', 'Tape Created', 'Date Archived'] # date columns
NUMS = ['Tape Size', 'Tape Used'] # number columns
BOOL = ['Worm'] # bool columns

def parse(file, dateRange, sort, search):
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
        tape['PoolEntryDate-Datetime'] = PoolEntryDate_time.replace(microsecond= 0) # ignore microsecond
        
            
    tapes_ = []
    if dateRange: # case sensitive, can be done in any of the date columns
        # parse dateRange
        r_type = dateRange.split(':')
        if len(r_type) == 1: # empty col
            print('No column found. Defaulting to "Pool Entry Date" for dateRange')
            col = "Pool Entry Date"
        else:
            col, dateRange = r_type[0], r_type[1].strip()
        try:
            start, end = dateRange.split('-')
            start = datetime.strptime(start, '%Y/%m/%d')
            end = datetime.strptime(end, '%Y/%m/%d')
        except Exception as e:
            print('Invalid Date Range format. Example: 2021/08/01-2021/08/26')
            return
        
        # eliminate tapes not in that date range
        for tape in tapes:
            if start <= tape[f'{col.replace(" ", "")}-Datetime'] <= end:
                #print(tape_time)
                tapes_.append(tape)
    
        tapes = tapes_
        
        if not tapes: # empty, nothing within that range
            print('NO TAPES FOUND')
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
    
    tapes.drop('PoolEntryDate-Datetime', axis = 1, inplace = True)
    
    tapes.columns = ['Barcode', 'Tape Size', 'Status', 'Pool ID', 'Pool Entry Date'] # change column names
    
    # reformat dates to remove ms? and -05:00 smthign
    tapes['Pool Entry Date'] = tapes['Pool Entry Date'].map(lambda x: x[:x.find('.')])
    
    # search
    if search:
        search = search.split(',')
        for s in search:
            s_ = s.split(':')
            col, cond = s_[0].strip(), s_[1].strip()
            if col not in tapes.columns:
                print(col, 'not a valid column')
                continue
            if col in DATES:
                print('Dates not supported in search. Can use dateRange instead')
                continue
            elif col in NUMS:
                cond = int(cond)
                tapes = tapes.loc[tapes[col] == cond]
            elif col in BOOL:
                if cond.lower() == 'false':
                    cond = False
                else:
                    cond = True
                tapes = tapes.loc[tapes[col] == cond]
            else:
                tapes = tapes.loc[tapes[col] == cond]
    
    print('Amazon Resource Name:', resName)
    #print(tapes.to_string(index = False))
    print(tabulate(tapes, headers = 'keys', tablefmt = "pretty", showindex = False))

def parse_all_report(file, dateRange, sort, search):
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
        tape['TapeCreated-Datetime'] = TapeCreatedDate_time
        
    tapes_ = []
    if dateRange: # case sensitive, can be done in any of the date columns
        # parse dateRange
        r_type = dateRange.split(':')
        if len(r_type) == 1: # empty col
            print('No column found. Defaulting to "Pool Entry Date" for dateRange')
            col = "Pool Entry Date"
        else:
            col, dateRange = r_type[0], r_type[1].strip()
        try:
            start, end = dateRange.split('-')
            start = datetime.strptime(start, '%Y/%m/%d')
            end = datetime.strptime(end, '%Y/%m/%d')
        except Exception as e:
            print('Invalid Date Range format. Example: 2021/08/01-2021/08/26')
            return
        
        # eliminate tapes not in that date range
        for tape in tapes:
            if start <= tape[f'{col.replace(" ", "")}-Datetime'] <= end:
                #print(tape_time)
                tapes_.append(tape)
    
        tapes = tapes_
        
        if not tapes: # empty, nothing within that range
            print('NO TAPES FOUND')
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
                     'PoolEntryDate-Datetime', 'TapeCreated-Datetime'] # change column names
    
    if sort == 'Tape Created':
        tapes.sort_values(by = ['TapeCreated-Datetime', 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort == 'Pool Entry Date':
        tapes.sort_values(by = ['PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort.lower().title() in tapes.columns: # non dates
        # sorts by parameter and then date
        tapes.sort_values(by = [sort.lower().title(), 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    else:
        print('INVALID SORT PARAMETER')
        return
    
    tapes.drop('PoolEntryDate-Datetime', axis = 1, inplace = True)
    tapes.drop('TapeCreated-Datetime', axis = 1, inplace = True)
    
    # reformat dates to remove ms? and -05:00 smthign
    tapes['Pool Entry Date'] = tapes['Pool Entry Date'].map(lambda x: x[:x.find('.')])
    tapes['Tape Created'] = tapes['Tape Created'].map(lambda x: x[:x.find('.')])
    
    # reorder columns
    tapes.columns = ['Barcode', 'Tape Created', 'Tape Size', 'Status', 'Tape Used', 'Pool ID', 'Worm', 'Pool Entry Date'] # change column names
    tapes = tapes[['Barcode', 'Tape Size', 'Tape Used', 'Status', 'Pool ID', 'Worm','Pool Entry Date', 'Tape Created']]
    
    # search
    if search:
        search = search.split(',')
        for s in search:
            s_ = s.split(':')
            col, cond = s_[0].strip(), s_[1].strip()
            if col not in tapes.columns:
                print(col, 'not a valid column')
                continue
            if col in DATES:
                print('Dates not supported in search. Can use dateRange instead')
                continue
            elif col in NUMS:
                cond = int(cond)
                tapes = tapes.loc[tapes[col] == cond]
            elif col in BOOL:
                if cond.lower() == 'false':
                    cond = False
                else:
                    cond = True
                tapes = tapes.loc[tapes[col] == cond]
            else:
                tapes = tapes.loc[tapes[col] == cond]
    
    print('Amazon Resource Name:', resName)
    #print(tapes.to_string(index = False))
    print(tabulate(tapes, headers = 'keys', tablefmt = "pretty", showindex = False))
    
def parse_archived_report(file, dateRange, sort, search):
    # parse the text file as dictionary
    d = json.load(open(file, 'r'))
    # get first value which is a list of tapes. assuming theres only one key, value in txt file.
    # {Tapes: [...]} or {TapeArchives: [...]} or {TapeInfos: [...]}
    tapes = d[next(iter(d))]
    
    # parse datetime, into actual datetime
    for tape in tapes:
        PoolEntryDate_time = datetime.strptime(tape['PoolEntryDate'][: tape['PoolEntryDate'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        DateArchived_time =  datetime.strptime(tape['CompletionTime'][: tape['CompletionTime'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        TapeCreatedDate_time = datetime.strptime(tape['TapeCreatedDate'][: tape['TapeCreatedDate'].rfind('-')], '%Y-%m-%dT%H:%M:%S.%f')
        # just ignored the part after the date; 2021-10-14T14:16:11.709000-04:00
        # cuz idk what it is
        tape['PoolEntryDate-Datetime'] = PoolEntryDate_time
        tape['DateArchived-Datetime'] = DateArchived_time
        tape['TapeCreated-Datetime'] = TapeCreatedDate_time
        
    tapes_ = []
    if dateRange: # case sensitive, can be done in any of the date columns
        # parse dateRange
        r_type = dateRange.split(':')
        if len(r_type) == 1: # empty col
            print('No column found. Defaulting to "Pool Entry Date" for dateRange')
            col = "Pool Entry Date"
        else:
            col, dateRange = r_type[0], r_type[1].strip()
        try:
            start, end = dateRange.split('-')
            start = datetime.strptime(start, '%Y/%m/%d')
            end = datetime.strptime(end, '%Y/%m/%d')
        except Exception as e:
            print('Invalid Date Range format. Example: 2021/08/01-2021/08/26')
            return
        
        # eliminate tapes not in that date range
        for tape in tapes:
            if start <= tape[f'{col.replace(" ", "")}-Datetime'] <= end:
                #print(tape_time)
                tapes_.append(tape)
    
        tapes = tapes_
        
        if not tapes: # empty, nothing within that range
            print('NO TAPES FOUND')
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
                     'PoolEntryDate-Datetime', 'DateArchived-Datetime', 'TapeCreated-Datetime'] # change column names
    
    if sort == 'Tape Created':
        tapes.sort_values(by = ['TapeCreated-Datetime', 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort == 'Date Archived':
        tapes.sort_values(by = ['DateArchived-Datetime', 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort == 'Pool Entry Date':
        tapes.sort_values(by = ['PoolEntryDate-Datetime'], ascending = True, inplace = True)
    elif sort.lower().title() in tapes.columns: # non dates
        # sorts by parameter and then date
        tapes.sort_values(by = [sort.lower().title(), 'PoolEntryDate-Datetime'], ascending = True, inplace = True)
    else:
        print('INVALID SORT PARAMETER')
        return
    
    tapes.drop('PoolEntryDate-Datetime', axis = 1, inplace = True)
    tapes.drop('DateArchived-Datetime', axis = 1, inplace = True)
    tapes.drop('TapeCreated-Datetime', axis = 1, inplace = True)
    
    # reformat dates to remove ms? and -05:00 smthign
    tapes['Date Archived'] = tapes['Date Archived'].map(lambda x: x[:x.find('.')])
    tapes['Pool Entry Date'] = tapes['Pool Entry Date'].map(lambda x: x[:x.find('.')])
    tapes['Tape Created'] = tapes['Tape Created'].map(lambda x: x[:x.find('.')])
    
    # reorder columns
    tapes.columns = ['Barcode', 'Tape Created', 'Tape Size', 'Date Archived', 'Status', 'Tape Used', 'Pool ID', 'Worm', 'Pool Entry Date'] # change column names
    tapes = tapes[['Barcode', 'Tape Size', 'Tape Used', 'Status', 'Pool ID', 'Worm', 'Date Archived', 'Pool Entry Date', 'Tape Created']]
    
    # search
    if search:
        search = search.split(',')
        for s in search:
            s_ = s.split(':')
            col, cond = s_[0].strip(), s_[1].strip()
            if col not in tapes.columns:
                print(col, 'not a valid column')
                continue
            if col in DATES:
                print('Dates not supported in search. Can use dateRange instead')
                continue
            elif col in NUMS:
                cond = int(cond)
                tapes = tapes.loc[tapes[col] == cond]
            elif col in BOOL:
                if cond.lower() == 'false':
                    cond = False
                else:
                    cond = True
                tapes = tapes.loc[tapes[col] == cond]
            else:
                tapes = tapes.loc[tapes[col] == cond]
    
    print('Amazon Resource Name:', resName)
    #print(tapes.to_string(index = False))
    print(tabulate(tapes, headers = 'keys', tablefmt = "pretty", showindex = False))
    
if __name__ == '__main__':
    d = json.load(open(FLAGS.file, 'r'))
    file_type = next(iter(d))
    if file_type == 'Tapes': # all-tape-list-report
        parse_all_report(file = FLAGS.file, dateRange = FLAGS.dateRange, sort = FLAGS.sort, search = FLAGS.search)
    elif file_type == 'TapeArchives': # aws-archived-tape-report
        parse_archived_report(file = FLAGS.file, dateRange = FLAGS.dateRange, sort = FLAGS.sort, search = FLAGS.search)
    elif file_type == 'TapeInfos': # tape-list
        parse(file = FLAGS.file, dateRange = FLAGS.dateRange, sort = FLAGS.sort, search = FLAGS.search)