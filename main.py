import numpy as np

# import Gmsh
GmshFileName_Str = "tri2d.msh"
GmshFile_List = []
with open(GmshFileName_Str) as inputfile:
    for line in inputfile:
        GmshFile_List.append(line.strip().split(' '))
IndexInit_Nodes = [i for i, s in enumerate(GmshFile_List) if '$Nodes' in s]
IndexEnd_Nodes = [i for i, s in enumerate(GmshFile_List) if '$EndNodes' in s]
IndexInit_Eles = [i for i, s in enumerate(GmshFile_List) if '$Elements' in s]
IndexEnd_Eles = [i for i, s in enumerate(GmshFile_List) if '$EndElements' in s]
NodeN = int(GmshFile_List[IndexInit_Nodes[0]+1][0])
EleN = int(GmshFile_List[IndexInit_Eles[0]+1][0])
Node_Array = np.zeros((NodeN, 4))

Temp_EleN = 2
Ele_Array = np.zeros((EleN, Temp_EleN), dtype=int)
for Row in range(EleN):
    for Col in range(Temp_EleN):
        Ele_Array[Row, Col] = int(GmshFile_List[IndexInit_Eles[0]+2+Row][Col])
# remove elements of EleType == 15 and 1.
# 15: 1-node point; 1: 2-node line.
EleType15Index = np.where(Ele_Array[:, 1] == 15)[0]
EleType1Index = np.where(Ele_Array[:, 1] == 1)[0]
EleRemoveN = np.max(EleType1Index)+1

EleN = EleN - EleRemoveN
Temp_EleN = len(GmshFile_List[IndexEnd_Eles[0]-1]) # Mutiple type of elements, currently select the last element.
Ele_Array = np.zeros((EleN, Temp_EleN), dtype=int)
for Row in range(NodeN):
    for Col in range(4):
        Node_Array[Row, Col] = float(GmshFile_List[IndexInit_Nodes[0]+2+Row][Col])
for Row in range(EleN):
    for Col in range(Temp_EleN):
        Ele_Array[Row, Col] = int(GmshFile_List[IndexInit_Eles[0]+2+EleRemoveN+Row][Col])
Ele_Array[:, 0] = Ele_Array[:, 0] - EleRemoveN
# convert to the face based format
print "Currently only handle mesh of single type in single zone!"
print "1. Find all faces"
EleN = Ele_Array.shape[0]
EleNo_Array = Ele_Array[:, 0]
EleType = Ele_Array[0, 1]
EleTagN = Ele_Array[0, 2]
EleNode_Array = Ele_Array[:, 2+EleTagN+1:]
print "1. Get face list from element."
EleType_List = [[1, 2], [3, 2], [4, 2]]
EleFaceN = EleType_List[EleType-1][0]
FaceNodeN = EleType_List[EleType-1][1]
EleFace_Array = np.zeros((EleN, EleFaceN, FaceNodeN), dtype=int)
EleNodeRoll_Array = np.roll(EleNode_Array, 1, axis=1)
for EleI in range(EleN):
    for FaceI in range(EleFaceN-1):
        EleFace_Array[EleI, FaceI, :] = EleNode_Array[EleI, FaceI:FaceI+2]
    FaceI = EleFaceN-1
    EleFace_Array[EleI, FaceI, :] = EleNodeRoll_Array[EleI, 0:2]
print "2. Sort node list in each face; check if match."
EleFaceSort_Array = np.sort(EleFace_Array)
EleFace2D_Array = np.reshape(EleFace_Array, (EleN*EleFaceN, FaceNodeN))
FaceEle2D_Array = np.zeros((EleN*EleFaceN, 2), dtype=int)
FaceInterior_List = []
for EleI in range(EleN):
    FaceEle2D_Array[EleI*EleFaceN:(EleI+1)*EleFaceN, 0] = EleI + 1
    for EleJ in range(EleI+1, EleN):
        # print 'EleI: ', EleI, '; ', 'EleJ: ', EleJ
        for RollLen in range(1, EleFaceN):
            MatchIndex_Tuple = np.where(np.all(np.isclose(EleFaceSort_Array[EleI, :, :], np.roll(EleFaceSort_Array[EleJ, :, :], RollLen, axis=0)), axis=1))
            if MatchIndex_Tuple[0].size == 1: # Existing element means matched faces. Get the index by RollLen
                # Matched face is EleFaceSort_Array[0, MatchIndex[0][0], :] or say EleFaceSort_Array[1, MatchIndex[0][0]-RollLen, :]
                MatchIndex = MatchIndex_Tuple[0][0]
                # print EleFaceSort_Array[EleJ, MatchIndex-RollLen, :]
                # record elements no for current face
                FaceEle2D_Array[EleI*EleFaceN+MatchIndex, :] = [EleI+1, EleJ+1]
                # delete redundant face in Element EleJ
                FaceInterior_List.append(EleJ*EleFaceN+MatchIndex-RollLen)
                break
FaceEle2D_Array = np.delete(FaceEle2D_Array, FaceInterior_List, axis=0)
EleFace2D_Array = np.delete(EleFace2D_Array, FaceInterior_List, axis=0)
FaceN = FaceEle2D_Array.shape[0]
Face_Array = np.concatenate((np.arange(FaceN, dtype=int).reshape((FaceN,1))+1, np.zeros((FaceN,1), dtype=int)+FaceNodeN, EleFace2D_Array, FaceEle2D_Array), axis=1)

print Face_Array
# write to cgns file


