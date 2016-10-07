
# because exporting to csv is not doable from the cluster, use this.
# input should be 
# 1) a file, where filename = the table to which you want to upload to
# 2) another file, filename.types with K space delimited letters, where K = # of columns
#  if the n-th letter is s , then that column expects a string and the respective value
#   will be wrapped with single quotes in the query

import sys
import os

def parseFile(filename):
    fieldtypes = []
    fileobject = open(filename+".types",'r')
    line = fileobject.readline()
    fieldtypes = line.split()
    print(fieldtypes)
    
    lines = []
    fileobject = open(filename,'r')
    
    
    for line in fileobject:
        lines.append(line)
    # drop last 3 junk lines
    del lines[-2:]
    # drop 1st junk line
    del lines[0]
    # get column names
    columnstrings = lines[0].split("|")
    columnnames = []
    for col in columnstrings:
        columnnames.append(col.strip())
    del lines[0]
    
    # measure column lengths
    entrylengths = []
    columnstrings = lines[0].split("+")
    for col in columnstrings:
        entrylengths.append(len(col))
    del lines[0]

    # get entries per column
    entriesPerColumn = []
    for i in range(len(columnnames)):
        entriesPerColumn.append([])
        
    startingPoint = 0
    for line in lines:
        startingPoint = 0
        linelen=len(line)
        for c in range(len(columnnames)):
            element = line[startingPoint:startingPoint + entrylengths[c]] 
            entriesPerColumn[c].append( element.strip())
            startingPoint += entrylengths[c] + 1;
            
    
    fileobject.close()
    # construct Queries
    outfilename = "/home/npittaras/Documents/project/dev/backup/backup_insertion_queries"
    fileobject = open(outfilename,"w")
    print("Writing to " + outfilename);
    
    queries = []
    
    for l in range(len(lines)):
        query = ""
        query += "insert into  " + os.path.basename(filename) + "( "
        for col in columnnames:
            query += col+","
        query = query[:-1] + ") values (" # drop last comma
        for entryidx in range(len(entriesPerColumn)):
            # some elements have to be processed, like wrap with ''
            processed = entriesPerColumn[entryidx][l]
            if fieldtypes[entryidx] == 's':
                processed = "'" + processed + "'"
            query+= processed +","
                
        query =  query[:-1] +  ");\n"
        fileobject.write(query)

    fileobject.close();
    return (columnnames, entrylengths, lines)
    
def main():
    if len(sys.argv) < 2:
        print("Need an argument.")
        return
    print("Provided " + str(len(sys.argv)) + " args . ")
    filename = sys.argv[1]
    print("Filename:" + filename)
    (columnnames,entrylengths,lines) =  parseFile(filename)


if __name__ == "__main__":
    main()
