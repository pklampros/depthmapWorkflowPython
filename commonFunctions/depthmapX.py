def getAxmanesqueCMapLinear():
    from matplotlib.colors import LinearSegmentedColormap
    axmanesqueCols = [
        [ 51,  51, 221], #  0x003333DD, // 0 blue #  
        [ 51, 136, 221], #  0x003388DD, // 1      #  
        [ 34, 204, 221], #  0x0022CCDD, // 2      #  
        [ 34, 204, 187], #  0x0022CCBB, // 3      #  
        [ 34, 221, 136], #  0x0022DD88, // 4      #  
        [136, 221,  34], #  0x0088DD22, // 5      # 
        [187, 204,  34], #  0x00BBCC22, // 6      # 
        [221, 204,  34], #  0x00DDCC22, // 7      # 
        [221, 136,  51], #  0x00DD8833, // 8      # 
        [221,  51,  51] #  0x00DD3333, // 9 red  # 
    ]
    ncolpart = 1.0/(len(axmanesqueCols) - 1)
    cdict = {'red':   [[0 * ncolpart, axmanesqueCols[0][0]/255.0, axmanesqueCols[0][0]/255.0],
                       [1 * ncolpart, axmanesqueCols[1][0]/255.0, axmanesqueCols[1][0]/255.0],
                       [2 * ncolpart, axmanesqueCols[2][0]/255.0, axmanesqueCols[2][0]/255.0],
                       [3 * ncolpart, axmanesqueCols[3][0]/255.0, axmanesqueCols[3][0]/255.0],
                       [4 * ncolpart, axmanesqueCols[4][0]/255.0, axmanesqueCols[4][0]/255.0],
                       [5 * ncolpart, axmanesqueCols[5][0]/255.0, axmanesqueCols[5][0]/255.0],
                       [6 * ncolpart, axmanesqueCols[6][0]/255.0, axmanesqueCols[6][0]/255.0],
                       [7 * ncolpart, axmanesqueCols[7][0]/255.0, axmanesqueCols[7][0]/255.0],
                       [8 * ncolpart, axmanesqueCols[8][0]/255.0, axmanesqueCols[8][0]/255.0],
                       [9 * ncolpart, axmanesqueCols[9][0]/255.0, axmanesqueCols[9][0]/255.0]],
             'green': [[0 * ncolpart, axmanesqueCols[0][1]/255.0, axmanesqueCols[0][1]/255.0],
                       [1 * ncolpart, axmanesqueCols[1][1]/255.0, axmanesqueCols[1][1]/255.0],
                       [2 * ncolpart, axmanesqueCols[2][1]/255.0, axmanesqueCols[2][1]/255.0],
                       [3 * ncolpart, axmanesqueCols[3][1]/255.0, axmanesqueCols[3][1]/255.0],
                       [4 * ncolpart, axmanesqueCols[4][1]/255.0, axmanesqueCols[4][1]/255.0],
                       [5 * ncolpart, axmanesqueCols[5][1]/255.0, axmanesqueCols[5][1]/255.0],
                       [6 * ncolpart, axmanesqueCols[6][1]/255.0, axmanesqueCols[6][1]/255.0],
                       [7 * ncolpart, axmanesqueCols[7][1]/255.0, axmanesqueCols[7][1]/255.0],
                       [8 * ncolpart, axmanesqueCols[8][1]/255.0, axmanesqueCols[8][1]/255.0],
                       [9 * ncolpart, axmanesqueCols[9][1]/255.0, axmanesqueCols[9][1]/255.0]],
             'blue':  [[0 * ncolpart, axmanesqueCols[0][2]/255.0, axmanesqueCols[0][2]/255.0],
                       [1 * ncolpart, axmanesqueCols[1][2]/255.0, axmanesqueCols[1][2]/255.0],
                       [2 * ncolpart, axmanesqueCols[2][2]/255.0, axmanesqueCols[2][2]/255.0],
                       [3 * ncolpart, axmanesqueCols[3][2]/255.0, axmanesqueCols[3][2]/255.0],
                       [4 * ncolpart, axmanesqueCols[4][2]/255.0, axmanesqueCols[4][2]/255.0],
                       [5 * ncolpart, axmanesqueCols[5][2]/255.0, axmanesqueCols[5][2]/255.0],
                       [6 * ncolpart, axmanesqueCols[6][2]/255.0, axmanesqueCols[6][2]/255.0],
                       [7 * ncolpart, axmanesqueCols[7][2]/255.0, axmanesqueCols[7][2]/255.0],
                       [8 * ncolpart, axmanesqueCols[8][2]/255.0, axmanesqueCols[8][2]/255.0],
                       [9 * ncolpart, axmanesqueCols[9][2]/255.0, axmanesqueCols[9][2]/255.0]]}


    depthmapAxmanesque = LinearSegmentedColormap('depthmapAxmanesque', segmentdata=cdict, N=256)
    return depthmapAxmanesque
