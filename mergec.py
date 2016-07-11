# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 12:59:59 2016

@author: npittaras
"""

#
import sys


    
    
def readskip(filename):
    print("Reading " , filename)
    file = open(filename,"r")
    lines = []
    skipcounter = 1
    
    for line in file.readlines():
        if skipcounter <= 3:
            #print ("\t\tSkipping line ", skipcounter)
            skipcounter += 1
            continue
        line = line.strip()
        if len(line) > 0:
            if line[0] == "'":
                line = line[1:-1]
        lines.append(line)
    #print ("\tRead ", len(lines), " lines.")
    del lines[-1]
    del lines[-1]
    #print ("\tDropped last two : read ", len(lines), " lines.")    
    return lines
    
def parseSet(line):
    line = line.strip()
    if len(line) == 0:
        return line
    print("\n\nline to parse: [",line,"]")
    if line == "null":
        return []
    line = line[1:-1]     # drop { , }

    tokens = line.split(',')
    elements = []
    for token in tokens:
        tok = token.strip()
        if tok[0] == "'":
            tok = tok[1:-1]
        elements.append(tok)
        
    return elements
    
    
def readskipset(filename):
    print("Reading sets" , filename)
    file = open(filename,"r")
    lines = []
    skipcounter = 1
    
    for line in file.readlines():
        if skipcounter <= 3:
            print ("\t\tSkipping line ", skipcounter)
            skipcounter += 1
            continue
        lines.append(parseSet(line))
        print ("\tRead ", len(lines[-1]), " set members for fileline ", skipcounter,":")
        for l in lines[-1]:
            print ("[",l,"]")
    # drop last two lines
    del lines[-1]
    del lines[-1]
    print ("\tDropped last two : read ", len(lines), " lines.")    
    return lines




def getBBox(placeName,places_pplc,bboxes_ppcl):
    for i in range(len(places_pplc)):
        if placeName == places_pplc[i]:
            return bboxes_ppcl[i]
    print("ERROR: place/bbox for ",placeName, "wasnt found.")
    return []

# This method constructs on CQL map object ( a tuple)
# for each location, as LocationName : GeometryFromPopeye
def constructQuery_singlePairObj(event_ids,placenamesets,bboxessets):
    # diff table?
    f = open("location_merge_queries_singlepair","w")
    # debug files
    db = open("places_per_event_singlepair.debug","w")
    for e in range(len(event_ids)):
        wasSet = 0
        mapstr = ""
        for p in range(len(placenamesets[e])):
            place = placenamesets[e][p]
            db.write(place + " ")
            if wasSet == 0:
                mapstr = "{"
                wasSet = 1
            else:
                mapstr += ", "
            mapstr += "'"+ place + "' : '" + bboxessets[e][p] +"'";
        mapstr += "}"
        if wasSet == 1:
            query = "update events set place_mappings = place_mappings + " + mapstr + " where event_id = '" + event_ids[e] + "' ; ";
            
            f.write(query)
            f.write("\n")
        db.write("\n")
            
    f.close()
    
    db.close();
    print("Done.")  

# function to parse a geometry string :
# [{"type":"Polygon","coordinates":[[[c11,c12], ... ,[c51,c52]]]}]
def parseGeom(geom):
    # drop wrapping [{}]
    maps = []
    print("Geometry is :",geom)
    geom = geom[2:-2]
    # decided to rename the "splitcolon" var -> worst var. name evar
    splitc = geom.split(':') # should be len3 :[ "type", "Typename", "geometry:coords[....]]
    assert (len(splitc) == 3, "Split geometry by : should yield 3 tokens");
    assert (splitc[0]=='"type"','First geometry item by : should be "type" but it is ' + splitc[0])
    split2 = splitc[1].split(',') # get TYPE, "coordinates"
    assert (len(split2) == 2, "Split 2nd token by , should yield 2 tokens");
    assert (split2[1]=='"coordinates"','First geometry item by : should be "coordinates" but it is ' + split2[1])
    geometryType = split2[0]
    coords = splitc[-1]
    coords = coords[2:-2] # drop [[]] wrapper
    coords = coords.split('],')
    numcoords =     len(coords);
    coordTuples = []
    for i in range(numcoords):
        nums = coords[i].split(',')
        assert(nums[0] == '[','Did not find [ in coordinate pair start - sth''s wrong')
        nums[0] = nums[0][1:]
        if i == numcoords -1:
            nums[1] = nums[1][0:-1]
        coordTuples.append(nums)
    
    # put the numbers in a per-pair comma delimited string
    # leave the above in case we need it for another format
    coordinates = ""
    for i in range(numcoords):
        if i != 0:
            coordinates += ","
        coordinates += coordTuples[i][0] + " " + coordTuples[i][1]
    
    return (geometryType, coordinates)
    


def constructQuery_multiPairObj(event_ids, placenamesets, bboxessets):
    debubPrefix = "debugtest_"
    # diff table?
    f = open(debubPrefix + "location_merge_queries_multipair","w")
    # debug files
    db = open(debubPrefix + "places_per_event_multipair.debug","w")
    
    for e in range(len(event_ids)):
        wasSet = 0
        mapstr = ""
        eventMap = []        # Map as in CQL map
        for p in range(len(placenamesets[e])):
            place = placenamesets[e][p]
            db.write(place + " ")
            eventMap.append(['"locationName"','"' + place + '"'])
            if wasSet == 0:
                mapstr = "{"
                wasSet = 1

            
            if  bboxessets[e][p] == "null":
                mapstr += "'"+ place + "' : '" + bboxessets[e][p] +"'";
            else:
                (gtype,coords) = parseGeom(bboxessets[e][p])
                eventMap.append(['"type"',gtype])
                eventMap.append(['"coordinates"','"(' + coords + ')"'])
                
            # the supermap for the current location is complete : it's 3 CQL maps
            # locationName :name, type :geomtype, coordinates: (n1 n2, n3 n4, ..., n9 n10)
            assert(len(eventMap) == 3,"Event map of length =/= 3!")
            
        # populate mapstr
        # loc. coutner to enclose each location in {}
        locationCounter = 0
        for e in range(len(eventMap)):
            if locationCounter = 0:
                mapstr+="{"
            if e > 0 and e < len(eventMap):
                mapstr += ","
            obj = eventMap[e]
            print (mapstr)
            mapstr += obj[0] + ":" + obj[1]
            if locationCounter == 3:
                mapstr+="}"
                locationCounter = 0
                
                
        mapstr += "}"
        if wasSet == 1:
            query = "update events set place_mappings = place_mappings + " + mapstr + " where event_id = '" + event_ids[e] + "' ; ";
            
            f.write(query)
            f.write("\n")
        db.write("\n")
            
    f.close()
    
    db.close();
    print("Done.")  
    
    
def main():

    argv = []
    inputfile = open(sys.argv[1],"r")
    for arg in inputfile.readlines():
        argv.append(arg)
        argv[-1] = argv[-1].strip()
        
    argv.insert(0,[])
    # Read
    event_ids = readskip(argv[1])
    event_sourceurls = readskipset(argv[2])
    pplc_entryurls = readskip(argv[3])
    pplc_bbox = readskip(argv[4])
    entryurls = readskip(argv[5])
    places = readskipset(argv[6])
    pplc_places = readskip(argv[7])
    

    placenamesets = []
    bboxessets = []
    for eventIndex in range(len(event_ids)):
        srcurl = event_sourceurls[eventIndex]
        placenamesets.append([])
        bboxessets.append([])
        srcIndex = -1
        print ("event # ", eventIndex+1,"/",len(event_sourceurls), ": [" , event_ids[eventIndex], "]")
        # for each source url to that event
        for eventsrc in srcurl:
            srcIndex +=1
            print("\tsrc ",srcIndex+1,"/",len(srcurl),":",eventsrc)
            found = 0
            # scan all source urls in the per-place table
            for s in range(len(entryurls)):
                
                
                # if we found it, get the place name and its bbox
                # we have to search the urls in news_articles,NOT PER PLACE
                #- for some reason they are never found there
                # also that would get ONE place per source url
                # => the entry_url in news_per_place is useless?
                #print("checkin " , entryurls[s])
                
                if entryurls[s] == eventsrc:
                    print ("Found src at position ",s," place(s) :",places[s])
                    found = 1
                    # we found it at the s-th position
                    # get the places corresponding to that url
                    # for each place in that set, find the bbox
                    for eventPlaceIdx in range(len(places[s])):
                        
                        placename = places[s][eventPlaceIdx];
                        placenamesets[eventIndex].append(placename)
                        bbox = getBBox(placename,pplc_places,pplc_bbox)
                        bboxessets[eventIndex].append(bbox)
            if found == 0:
                print(">>> Did not find ",eventsrc)

                    
    # here we can construct the query that will enter the data
    # into cassandra
    
    #constructQuery_singlePairObj(event_ids, placenamesets, bboxessets)
  
    constructQuery_multiPairObj(event_ids, placenamesets, bboxessets)

    
    
    


    
    # no need to delimit!

    # some text edotprs fuck up the <null> entry (like sublime)    
    
    # construct a query per 
    
# place_mappings is what we wanna fill    
    
   # for line in eventsf.readlines():
   #     line = strip(line)
    
    
     
    

if __name__ == "__main__":
    main()