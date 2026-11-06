"""Stream the DOL OFLC LCA xlsx (one 500 MB sheet) to CSV with openpyxl read-only, keeping only employer / worksite / NAICS / status columns.
Worker, attorney, preparer and employer point-of-contact columns are never read out (AGENTS §6). Prints the row count so it can be checked
against an independent count of <row> elements (DuckDB read_xlsx silently returned 118,580 of 563,689 rows on this file).
Usage: uv run --with openpyxl python3 xlsx_to_csv.py IN.xlsx OUT.csv"""
import csv,sys
from openpyxl import load_workbook
KEEP=['CASE_NUMBER','CASE_STATUS','RECEIVED_DATE','DECISION_DATE','VISA_CLASS','EMPLOYER_NAME','TRADE_NAME_DBA','EMPLOYER_ADDRESS1','EMPLOYER_ADDRESS2','EMPLOYER_CITY','EMPLOYER_STATE','EMPLOYER_POSTAL_CODE','EMPLOYER_COUNTRY','NAICS_CODE','WORKSITE_ADDRESS1','WORKSITE_ADDRESS2','WORKSITE_CITY','WORKSITE_COUNTY','WORKSITE_STATE','WORKSITE_POSTAL_CODE','TOTAL_WORKSITE_LOCATIONS']
def main(src,dst):
 wb=load_workbook(src,read_only=True);ws=wb.active;it=ws.iter_rows(values_only=True);head=[str(h) for h in next(it)];ix=[head.index(k) for k in KEEP];n=0
 with open(dst,'w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(KEEP)
  for r in it:
   if r and any(c is not None for c in r):w.writerow(['' if r[i] is None else r[i] for i in ix]);n+=1
 print('data rows',n,'columns in sheet',len(head))
if __name__=='__main__':main(*sys.argv[1:3])
