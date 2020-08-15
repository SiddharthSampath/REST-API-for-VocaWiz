import xlrd
loc = ("Mywords.xlsx")
wb = xlrd.open_workbook(loc) 
sheet = wb.sheet_by_index(0)
words = []
meanings = []
examples = []
completed = [] 
for i in range(sheet.nrows): 
   words.append(sheet.cell_value(i, 0))
   meanings.append(sheet.cell_value(i, 1)) 
   examples.append(sheet.cell_value(i, 2)) 
   completed.append(sheet.cell_value(i, 3))

print("Words = ", words) 
print("Meanings = ", meanings) 
print("Examples = ", examples) 
print("Completed = ", completed) 