import pandas as pd


# Check file Import and get Json Value
def useFileImport(filePath, fileFilter, customType):
    flName = filePath.filename
    flType = flName.split('.')[-1]
    # cek file type allowed

    if flType not in fileFilter:
        return {"error": "Maaf jenis file tidak didukung"}
    else:
        data = []
        # If file Excel
        if flType[0:2] == 'xl':
            dataExcel = pd.read_excel(
                filePath, index_col=0, dtype=customType).to_dict(orient='records')
            for i in dataExcel:
                data.append(i)
        # if file Json
        if flType[0:2] == 'js':
            dataJson = pd.read_json(
                filePath, dtype=customType).to_dict(orient='index')
            for i in dataJson:
                data.append(dataJson[i])
        # if file Csv
        if flType[0:2] == 'cs':
            dataCsv = pd.read_csv(
                filePath, dtype=customType).to_dict(orient='index')
            for i in dataCsv:
                data.append(dataCsv[i])
        # Final Result
        status = {
            "fileType": flType,
            "fileName": flName,
            "data": data
        }
    return status
