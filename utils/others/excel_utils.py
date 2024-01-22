# generate a excel


import openpyxl


def generate_excel(data, file_name):
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in data:
        ws.append(row)
    wb.save(file_name)
