import os
import platform
import subprocess
import geopandas
import pandas as pd
import numpy as np
import tempfile
import string
import random
from shapely.geometry import Point

def getDepthmapXcli():
    # this just selects the correct depthmapXcli from the lib folder, depending on the
    # depending on the operating system jupyter python is running on (darwin is macOS)
    
    if platform.system() == "Windows":
        depthmapXcli = "../lib/depthmapXcli.exe"
    elif platform.system() == "Darwin":
        depthmapXcli = "../lib/depthmapXcli.darwin"
    elif platform.system() == "Linux":
        depthmapXcli = "../lib/depthmapXcli.linux"
        # in linux it's necessary to make the cli executable
        new_mode = os.stat(depthmapXcli).st_mode | 0o100
        os.chmod(depthmapXcli,new_mode)
    else:
        raise ValueError('Unknown platform: ' + platform.system())
    return depthmapXcli


def importLines(lineMap, graphFileOut, cliPath = getDepthmapXcli()):
    gdf = lineMap.explode(index_parts=False)
    allCoordSizes = gdf.geometry.apply( lambda line: len(line.coords) != 2)
    if allCoordSizes.any():
        raise ValueError('The included map contains polylines, please break down to 2-point segments')
    lineCoords = gdf.geometry.apply( lambda line: line.coords).apply(np.ravel)
    df = pd.DataFrame(gdf[[col for col in gdf.columns if col != gdf._geometry_column_name]])
    df['x1'] = lineCoords.apply( lambda line: line[0])
    df['y1'] = lineCoords.apply( lambda line: line[1])
    df['x2'] = lineCoords.apply( lambda line: line[2])
    df['y2'] = lineCoords.apply( lambda line: line[3])
    with tempfile.NamedTemporaryFile(suffix='.tsv') as tmp:
        df.to_csv(tmp, sep='\t', index=False)
        subprocess.check_output([cliPath,
                             "-f",  tmp.name,
                             "-o",  graphFileOut,
                             "-m",  "IMPORT",
                             "-it", "data"])
        

def generateRandomCapString(n = 10):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))


def convertMap(graphFileIn, graphFileOut = None, newMapType = "axial", newMapName = generateRandomCapString(10),
               removeInputMap = False, copyAttributes = False, stubLengthToRemove = None,
               cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
    if newMapType not in ["drawing", "axial", "segment", "data", "convex"]:
        raise ValueError("Unknown map type: " + newMapType)
  
    params = [cliPath,
              "-f", graphFileIn,
              "-o", graphFileOut,
              "-m", "MAPCONVERT",
              "-co", newMapType,
              "-con", newMapName]
    if removeInputMap:
        params.append("-cir")
    if copyAttributes:
        params.append("-coc")
    if stubLengthToRemove is not None:
        params.extend(["-crsl", str(stubLengthToRemove)])

    subprocess.check_output(params)
    
    
    
def export(graphFileIn, fileOut, exportType,
                  cliPath = getDepthmapXcli()):
    subprocess.check_output([cliPath,
                             "-f", graphFileIn,
                             "-o", fileOut,
                             "-m", "EXPORT",
                             "-em", exportType])


def getPointmapData(graphFileIn, scale = 1, cliPath = getDepthmapXcli()):
    
    with tempfile.NamedTemporaryFile(suffix='.csv') as mapFile:
        export(graphFileIn, mapFile.name, "pointmap-data-csv", cliPath)
        dpm = processPointMap(mapFile, scale, ",")
        return(dpm);


def getPointmapLinks(graphFileIn, cliPath = getDepthmapXcli()):
    with tempfile.NamedTemporaryFile(suffix='.csv') as csvFile:
        export(graphFileIn, csvFile.name, "pointmap-links-csv", cliPath)
        links = read.csv(csvFile)
        return(links);


def getPointmapDataAndLinks(graphFileIn, scale = 1, cliPath = getDepthmapXcli()):
    with tempfile.NamedTemporaryFile(suffix='.csv') as mapFile, tempfile.NamedTemporaryFile(suffix='.csv') as linkFile:
        export(graphFileIn, mapFile.name, "pointmap-data-csv")
        export(graphFileIn, linkFile.name, "pointmap-links-csv")
        dpm = processPointMapAndLinks(mapFile, linkFile, scale, ",")
        return(dpm);

def refIDtoIndex(refID):
    i = refID >> 16;
    j = refID & 0x0000FFFF;
    return [i,j];

def processPointMap(filepath, scale = 1, sep = "\t"):
    pointMapData = pd.read_csv(filepath, sep=sep);
    pointMapData['x'] = pointMapData['x']*scale;
    pointMapData['y'] = pointMapData['y']*scale;
    ij = pd.DataFrame(np.transpose(refIDtoIndex(pointMapData['Ref'].values)), columns=['i', 'j'])
    pointMapData = pd.concat([pointMapData, ij], axis=1, sort=False)
    pointMapData['coords'] = list(zip(pointMapData.x, pointMapData.y))
    pointMapData['coords'] = pointMapData['coords'].apply(Point)
    dpm = geopandas.GeoDataFrame( pointMapData[list(set(list(pointMapData)) - set(["x","y"]))], geometry='coords')
    return dpm;

def processPointMapAndLinks(mapPath, linkPath = None, scale = 1, sep = "\t"):
    pointMap = processPointMap(mapPath, scale, sep)
    links = None
    if linkPath is not None:
        links = pd.read.csv(linkPath, sep = sep)
    return (pointMap, links)


def getShapeGraph(graphFileIn, cliPath = getDepthmapXcli()):
    with tempfile.NamedTemporaryFile(suffix='.mif') as mapFile:
        export(graphFileIn, mapFile.name, "shapegraph-map-mif", cliPath)
        ogr = geopandas.read_file(mapFile.name)
        return(ogr);


def getShapeGraphConnections(graphFileIn, cliPath = getDepthmapXcli()):
    with tempfile.NamedTemporaryFile(suffix='.csv') as connectionsFile:
        export(graphFileIn, connectionsFile.name, "shapegraph-connections-csv", cliPath)
        csv = pd.read_csv(connectionsFile.name, header = True, sep = ",")
        return(csv);


def getShapeGraphLinksUnlinks(graphFileIn, cliPath = getDepthmapXcli()):
    with tempfile.NamedTemporaryFile(suffix='.csv') as linksunlinksFile:
        export(graphFileIn, linksunlinksFile.name, "shapegraph-links-unlinks-csv", cliPath)
        csv = pd.read_csv(linksunlinksFile.name, header = True, sep = ",")
        return(csv);
    
    
def axialAnalysis(graphFileIn, graphFileOut = None, radii = ["n"], includeChoice = False,
                         includeLocal = False, includeIntermediateMetrics = False,
                         cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
    params = [cliPath,
              "-f", graphFileIn,
              "-o", graphFileOut,
              "-m", "AXIAL",
              "-xa", ",".join(radii)]
    if includeChoice:
        params.append("-xac")
    if includeLocal:
        params.append("-xal")
    if includeIntermediateMetrics:
        params.append("-xar")
        
    subprocess.check_output(params)


def segmentAnalysis(graphFileIn, graphFileOut = None, analysisType = "tulip", radii = ["n"],
                    radiusType = "metric", tulipBins = None, weightWithColumn = None,
                    includeChoice = False, cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn
        
    if analysisType not in ["tulip", "metric", "angular", "topological"]:
        raise ValueError("Unknown segment analysis type: " + analysisType)
    
    if radiusType not in ["steps", "metric", "angular"]:
        raise ValueError("Unknown radius type: " + radiusType)
    
    params = [cliPath,
              "-f", graphFileIn,
              "-o", graphFileOut,
              "-m", "SEGMENT",
              "-st", analysisType,
              "-sr",  ",".join(radii),
              "-srt", radiusType]
    
    if includeChoice:
        params.append("-sic")
    if tulipBins is not None:
        params.extend(["-stb", str(tulipBins)])
    if weightWithColumn is not None:
        params.extend(["-swa", str(weightWithColumn)])
    
    subprocess.check_output(params)

    
    

def createGrid(graphFileIn, graphFileOut = None, gridSize = 0.5,
                      cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
    params = [cliPath,
              "-f", graphFileIn,
              "-o", graphFileOut,
              "-m", "VISPREP",
              "-pg", str(gridSize)]
    
    subprocess.check_output(params)


def fillGrid(graphFileIn, graphFileOut = None, fillX = None, fillY = None,
                    cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
    if fillX is None:
        raise ValueError("At least one fill location must be provided (fillX is None)")
    if fillY is None:
        raise ValueError("At least one fill location must be provided (fillY is None)")
    if not isinstance(fillX, list):
        fillX = [fillX]
    if not isinstance(fillY, list):
        fillY = [fillY]
    if  len(fillX) == 0:
        raise ValueError("At least one fill location must be provided (fillX is empty)")
    if len(fillY) == 0:
        raise ValueError("At least one fill location must be provided (fillY is empty)")
    if len(fillX) != len(fillY):
        raise ValueError("fillX and fillY must have the same number of coordinates")
        
    with tempfile.NamedTemporaryFile(suffix='.tsv') as tmpPtz:
        
        li = np.transpose([fillX, fillY])
        dt = pd.DataFrame(li, columns=['x', 'y'])
        dt.to_csv(tmpPtz.name, index = False, sep = "\t")

        params = [cliPath,
                  "-f", graphFileIn,
                  "-o", graphFileOut,
                  "-m", "VISPREP",
                  "-pf", tmpPtz.name]

        subprocess.check_output(params)


def makeVGAGraph(graphFileIn, graphFileOut = None, maxVisibility = None, boundaryGraph = False,
                        cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
    params = [cliPath,
              "-f", graphFileIn,
              "-o", graphFileOut,
              "-m", "VISPREP",
              "-pm"]
    if maxVisibility is not None:
        params.extend(["-pr", str(maxVisibility)])
    if boundaryGraph:
        params.append("-pb")

    subprocess.check_output(params)


def unmakeVGAGraph(graphFileIn, graphFileOut = None, removeLinks = False,
                      cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
    params = [cliPath,
              "-f", graphFileIn,
              "-o", graphFileOut,
              "-m", "VISPREP",
              "-pu"]

    if removeLinks:
        params.append("-pl")
    
    subprocess.check_output(params)

    

def VGA(graphFileIn, graphFileOut = None, vgaMode = "visibility-global", radii = ["n"],
               cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
    if vgaMode not in ["isovist", "visibility-global", "visibility-local",
                       "metric", "angular", "thruvision"]:
        raise ValueError("Unknown segment VGA mode: " + vgaMode)
    
    params = [cliPath,
              "-f", graphFileIn,
              "-o", graphFileOut,
              "-m", "VGA",
              "-vr", ",".join(radii)]
              
    if vgaMode in ["isovist", "metric", "angular", "thruvision"]:
        params.extend(["-vm", vgaMode])
    elif vgaMode == "visibility-global":
        params.extend(["-vm", "visibility"])
        params.append("-vg")
    elif vgaMode == "visibility-local":
        params.extend(["-vm", "visibility"])
        params.append("-local")
    
    subprocess.check_output(params)


def linkMapCoords(graphFileIn, graphFileOut = None, linkFromX = None, linkFromY = None,
                  linkToX = None, linkToY = None, unlink = False, mapTypeToLink = "pointmaps",
                  cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
        
    if linkFromX is None:
        raise ValueError("At least one fill location must be provided (linkFromX is None)")
    if linkFromY is None:
        raise ValueError("At least one fill location must be provided (linkFromY is None)")
    if linkToX is None:
        raise ValueError("At least one fill location must be provided (linkToX is None)")
    if linkToY is None:
        raise ValueError("At least one fill location must be provided (linkToY is None)")
        
    if not isinstance(linkFromX, list):
        linkFromX = [linkFromX]
    if not isinstance(linkFromY, list):
        linkFromY = [linkFromY]
    if not isinstance(linkToX, list):
        linkToX = [linkToX]
    if not isinstance(linkToY, list):
        linkToY = [linkToY]
        
    if  len(linkFromX) == 0:
        raise ValueError("At least one fill location must be provided (linkFromX is empty)")
    if len(linkFromY) == 0:
        raise ValueError("At least one fill location must be provided (linkFromY is empty)")
    if  len(linkToX) == 0:
        raise ValueError("At least one fill location must be provided (linkToX is empty)")
    if len(linkToY) == 0:
        raise ValueError("At least one fill location must be provided (linkToY is empty)")
        
    if len(linkFromX) != len(linkFromY):
        raise ValueError("linkFromX and linkFromY must have the same number of coordinates")
    if len(linkToX) != len(linkToY):
        raise ValueError("linkToX and linkToY must have the same number of coordinates")
    if len(linkFromX) != len(linkToX):
        raise ValueError("linkFromX and linkToX must have the same number of coordinates")
        
    if mapTypeToLink not in ["pointmaps", "shapegraphs"]:
        raise ValueError("Unknown map type: " + mapTypeToLink)

    with tempfile.NamedTemporaryFile(suffix='.tsv') as tmpPtz:
        
        li = np.transpose([linkFromX, linkFromY, linkToX, linkToY])
        dt = pd.DataFrame(li, columns=['x1', 'y1', 'x2', 'y2'])
        dt.to_csv(tmpPtz.name, index = False, sep = "\t")

        params = [cliPath,
                  "-f", graphFileIn,
                 "-o", graphFileOut,
                 "-m", "LINK",
                 "-lmt", mapTypeToLink,
                 "-lm", "unlink" if unlink else "link",
                 "-lt", "coords",
                 "-lf", tmpPtz.name]


        subprocess.check_output(params)


def linkMapRefs(graphFileIn, graphFileOut = None, linkFrom = None, linkTo = None,
                mapTypeToLink = "pointmaps", unlink = False,
                cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
        
    if linkFrom is None:
        raise ValueError("At least one fill location must be provided (linkFrom is None)")
    if linkTo is None:
        raise ValueError("At least one fill location must be provided (linkTo is None)")
    if not isinstance(linkFrom, list):
        linkFrom = [linkFrom]
    if not isinstance(linkTo, list):
        linkTo = [linkTo]
    if  len(linkFrom) == 0:
        raise ValueError("At least one fill location must be provided (linkFrom is empty)")
    if len(linkTo) == 0:
        raise ValueError("At least one fill location must be provided (linkTo is empty)")
    if len(linkTo) != len(linkTo):
        raise ValueError("linkFrom and linkTo must have the same number of coordinates")
        
    if mapTypeToLink not in ["pointmaps", "shapegraphs"]:
        raise ValueError("Unknown map type: " + mapTypeToLink)

    with tempfile.NamedTemporaryFile(suffix='.tsv') as tmpPtz:
        
        li = np.transpose([linkFrom, linkTo])
        dt = pd.DataFrame(li, columns=['reffrom', 'refto'])
        dt.to_csv(tmpPtz.name, index = False, sep = "\t")


        params = [cliPath,
                  "-f", graphFileIn,
                 "-o", graphFileOut,
                 "-m", "LINK",
                 "-lmt", mapTypeToLink,
                 "-lm", "unlink" if unlink else "link",
                 "-lt", "refs",
                 "-lf", tmpPtz.name]

        subprocess.check_output(params)

        
        
def agentAnalysis(graphFileIn, graphFileOut = None, lookMode = "standard", timesteps = 5000,
                  releaseRate = 0.1, agentFOV = 16, agentSteps = 3, agentLife = 500,
                  originX = None, originY = None, locationSeed = 0, numberOfTrails = None,
                  outputType = "graph", cliPath = getDepthmapXcli()):
    if graphFileOut is None:
        graphFileOut = graphFileIn;
        
    if lookMode not in ["standard", "los-length", "occ-length", "occ-any", "occ-group-45",
                        "occ-group-60", "occ-furthest", "bin-far-dist", "bin-angle",
                        "bin-far-dist-angle", "bin-memory"]:
        raise ValueError("Unknown agent look mode: " + lookMode)
        
    if outputType not in ["graph", "gatecounts", "trails"]:
        raise ValueError("Unknown output type: " + outputType)

    params = [cliPath,
              "-f", graphFileIn,
              "-o", graphFileOut,
              "-m", "AGENTS",
              "-am", lookMode,
              "-ats", str(timesteps),
              "-arr", str(releaseRate),
              "-afov", str(agentFOV),
              "-asteps", str(agentSteps),
              "-alife", str(agentLife),
              "-alocseed", str(locationSeed),
              "-ot", outputType]
              
    if numberOfTrails is not None:
        params.extend(["-atrails", numberOfTrails])
              
    if originX is not None:
        with tempfile.NamedTemporaryFile(suffix='.tsv') as tmpPtz:
            if not isinstance(originX, list):
                originX = [originX]
            if not isinstance(originY, list):
                originY = [originY]
            li = np.transpose([originX, originY])
            dt = pd.DataFrame(li, columns=['x', 'y'])
            dt.to_csv(tmpPtz.name, index = False, sep = "\t")

            params.extend(["-alocfile", tmpPtz])
            subprocess.check_output(params)
  
    else:
        subprocess.check_output(params)