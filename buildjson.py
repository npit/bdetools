# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 15:33:19 2016
Creates a json file out of a CQL query result.
@author: npittaras
"""
import sys

def error(message):
    sys.stderr.write("error: %s\n" % message)
    sys.exit(1)
    
def countPipes(line):
    cols = 0
    columWidths = []
    widthcounter = 0
    for char in line:
        if char == '|':
            columWidths.append(widthcounter)
            widthcounter = 0
            cols += 1
        else:
            widthcounter +=1
    columWidths.append(widthcounter)
    return (cols,columWidths)

def fixtTokens(tokens,cols,colwidths):   
    
    fixedTokens = []
    tidx = -1;
    widx = 0;
    store = ""
    candidatelen = 0
    for t in tokens:
        store += t
        tidx+=1
        if len(store) == colwidths[widx]:
            print(len(store) , "=",colwidths[widx],"setting store to tok",len(fixedTokens), "candid. len:",candidatelen)
            fixedTokens.append(t)
            widx+=1
            candidatelen = 0
            store = ""
        else:
            store +="|"
            #candidatelen += len(store)+1
            print(len(store) , "!=",colwidths[widx],"updating store to a len of ",len(store), "candid. len:",candidatelen)
            

                    
    return fixedTokens

            
        
    return
def readquerydump(filename):
    f = open(filename,"r")
    linecount = 0
    data = []
    cols = 0
    colwidths = 0
    for line in f.readlines():
        linecount+=1
        if linecount == 1 or linecount == 3:
            continue
        elif linecount == 2:
            # count the number of | to determine number of cols
            (tcols,tcolwidths) = countPipes(line)
            colwidths = tcolwidths;
            cols = 1 + tcols;
            if cols < 1:
                print("*** Error : ",cols," columns in file ",filename)
                exit
            print(cols," columns in file ",filename)
            continue
        tokens = line.split('|')
        numtk = len(tokens)
        if numtk != cols:
            tokens = fixtTokens(tokens,cols,colwidths)
            numtk = len(tokens)
            if numtk != cols:
                print("*** Error : mismatch | Delimiter in line", linecount," in file ",filename)
                exit
        # strip the tokens off their whitespace
        print(tokens)
        for t in range(len(tokens)):
            tokens[t] = tokens[t].strip()


        data.append(tokens)
    
    # drop last 2 lines
    del data[-1]    
    del data[-1]    
    return data

def printjson(data):
    # pick the format u want
    event_popeye(data)

# popeye helpers
def wrap(s):
    s = '"' + str(s) + '"'
    return s

# YYYY-MM-DDThh:mm:ssΖ
def processdate(date):
    ref = "YYYY-MM-DDThh:mm:ss+0000"
    print (len(date), len(ref))
    fixdate = ""

    if len(date) == len(ref) -3: # seconds (:ss) are missing (probably)
        fixdate = date[0:-5] 
        fixdate += ":00+0000"

    return fixdate

def parseWrapped(L):
    element = ""
    c = L.pop()      # parse "
    c = L.pop() 
    while  c != '"':
        element += c
        c = L.pop()
    return element

def pop(L,num):
    for n in range(num):
        c = L.pop()
    return c

def parsegeometry(geom):
    # geom is:
    # {
    # 'France': 
    # '[
    # {"type":"Polygon","coordinates":[[
    # [72.6793899536133,46.4682693481445],[72.6793899536133,46.3693084716797],
    # [72.5312271118163,46.3693084716797],[72.5312271118163,46.4682693481445],
    # [72.6793899536133,46.4682693481445]
    # ]]
    # }
    #]'
    # , 
    # 'Paris': 
    # '[{"type":"Polygon","coordinates":[[
    # [2.36385679244989,48.8719177246094],[2.36385679244989,48.8480911254883],
    # [2.39907360076904,48.8480911254883],[2.39907360076904,48.8719177246094],
    # [2.36385679244989,48.8719177246094]
    #]]
    # }
    #]'
    # }



# {'Canada': '[{"type":"Polygon","coordinates":[[
# [51.7083549499512,15.0024843215942],[51.7083549499512,15.6775121688843],
# [51.1747894287109,15.6775121688843],[51.1747894287109,15.0024843215942],
# [51.7083549499512,15.0024843215942]]]}]', 'Iran':
#
    areas = []
    typevals = []
    coords = []
    S = []
    
    geom = geom[1:-1] # drop wraping {}
    geom = list(reversed(list(geom)))
    
    while 1:
        if not geom:
            break;
        c = geom.pop()
        if c == "'":
            # parce an area name
            area = ""
            c = geom.pop()
            while c != "'":
                area += c
                c = geom.pop()
            areas.append(area)
            pop(geom,4)     # parse :'[{ 
            geom.pop()      # parse {
            
            var = parseWrapped(geom) # parse "type"
            geom.pop()      # parse :
            typeval = parseWrapped(geom) # get the type value
            typevals.append(typeval)
            geom.pop()      # parse ,
            
            var = parseWrapped(geom) # parse "coordinates"
            pop(geom,3)        # parse : [[
            
            # parse coordinate value pairs in [] delim'd with commas
            coords.append([])
            geom.pop()        # initial [ 
            c = geom.pop()
            while  c != ']':    # if it's comma or number go on
                
                
                num1=""
                num2=""
                while c !=",":
                    num1+=c
                    c = geom.pop()
                c = geom.pop()
                while c !="]":
                    num2+=c
                    c = geom.pop()
                # closing ] of coord pair is consumed
                coords[-1].extend([num1, num2])
                # get new value
                c = geom.pop()
                if c == ",":
                    c = pop(geom,2) # .[
                    continue
            
            geom.pop()  # parse the 2nd closing ] of coordinates
            
            pop(geom,3)      # parse }]'
            
            if (len(geom) >0):
                c = pop(geom,1) # parse , '
                c =whitespace(geom)
                continue
    print ("Done parsing geometries.")
    return (areas, typevals, coords)
            

            
def whitespace(L):
    c = L[-1]
    while c == ' ' or c =='\t'  or c == '\n':
        c = L.pop()
        return c
    
def event_popeye(data):
    # FORMAT OF popeye.di.uoa.gr PROCESS
    # {"id":"1","title":"test event","eventDate":"2016-02-25T17:48:49+0000",
    # "referenceDate":"2016-02-25T17:48:49+0000",
    # "areas":[
    # {
    #    "name":"Athens",
    #    "geometry":
    #     {
    #       "type":"Polygon",
    #        "coordinates": 
    #               [[
    #                   [35.31,25.3],[35.31,19.25],[41.09,19.25],[41.09,25.3],[35.31,25.3]
    #               ]]
    #     }
    # } 
    # ] # areas
    # } # global
    
    # assume a column mapping table -> popeyejson
    # Current structure of event table:
    # event_id text PRIMARY KEY,
    # description text,
    # event_date text,
    # event_source_urls set<text>,
    # place_mappings map<text, text>,
    # title text,
    # tweet_post_ids set<bigint>

    eid = 0
    title = 1
    date = 2
    refdate = -1 # null
    geom = 4
    f = open("data.json","w")
    for l in range(len(data)):
        line = '{' + wrap("id") + ":" + wrap(data[l][eid]) + ',';
        line += wrap("title") + ":" + wrap(data[l][title]) + ",";
        pdate = processdate(data[l][date])
        line += wrap("eventDate") + ":" + wrap(pdate) + ",";
        if refdate == -1:
            rdate = "null";
        
        line += wrap("referenceDate") + ":"+ rdate + ",";
        line += wrap("areas") + ":";
        
        # locations & geometries
        geometry = data[l][geom];
        if geometry == "null":
            line +="null"
        else:
            line +=  "["
            
            (areas, types, coords) = parsegeometry(geometry);
            for a in range(len(areas)):
                if a > 0:
                    line += ","
                line += "{"
                line += wrap("name") + ":" + wrap(areas[a]) + ",";
                line += wrap("geometry") + ":" + "{";
                line += wrap("type") + ":" + wrap(types[a]) + ",";
                line += wrap("coordinates") + ":" + "[[";
                c = 0
                while c < (len(coords[a])):
                    if c != 0:
                        line +=","
                    line += "[" + coords[a][c] + "," + coords[a][c+1] + "]"
                    c += 2  
                line += "]]"; # end coordinates
                    
                line += "}"; # end geometry
                line += "}"  # end area
            line +=  "]"
        

        line += "}"; # json
        f.write(line + "\n");
    f.close();

def main():
    data = readquerydump(sys.argv[1])
    printjson(data)
    
    return

if __name__ == "__main__":
    main()