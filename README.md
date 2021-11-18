# whatever

python parse.py --file .\aws-all-tape-list-report.txt
python parse.py --file .\aws-all-tape-list-report.txt --search "Status: AVAILABLE"
python parse.py --file .\aws-all-tape-list-report.txt --dateRange "Tape Created: 2021/08/29-2021/09/24"
python parse.py --file .\aws-archived-tape-report.txt
python parse.py --file .\aws-archived-tape-report.txt --search "Worm: False, Pool ID: GLACIER" --sort "Tape Used"
python parse.py --file .\aws-archived-tape-report.txt --dateRange "Date Archived: 2021/10/01-2021/10/19"
python parse.py --file .\tape-list.txt
python parse.py --file .\tape-list.txt --sort Status
python parse.py --file .\tape-list.txt --search "Barcode: OXBK1F85BD"