import numpy as np

###########################################################
# Import Gmsh
# Gmsh file should be of the format ASCII
GmshFileName_Str = "tri2d.msh"
GmshFile_List = []
with open(GmshFileName_Str) as inputfile:
    for line in inputfile:
        GmshFile_List.append(line.strip().split(' '))
###########################################################
# Get the index of node section and element section
IndexInit_Nodes = [i for i, s in enumerate(GmshFile_List) if '$Nodes' in s]
IndexEnd_Nodes = [i for i, s in enumerate(GmshFile_List) if '$EndNodes' in s]
IndexInit_Eles = [i for i, s in enumerate(GmshFile_List) if '$Elements' in s]
IndexEnd_Eles = [i for i, s in enumerate(GmshFile_List) if '$EndElements' in s]
# Get the number of nodes and elements
NodeN = int(GmshFile_List[IndexInit_Nodes[0]+1][0])
EleN = int(GmshFile_List[IndexInit_Eles[0]+1][0])
Node_Array = np.zeros((NodeN, 4))
# However, currently, elements in Gmsh file include at least 3 types: 15, 1, 3(quad2d) or 2(tri2d).
Temp_EleN = 2 # set 2 to only include element no and type.
Ele_Array = np.zeros((EleN, Temp_EleN), dtype=int)
# Read all elements
for Row in range(EleN):
    for Col in range(Temp_EleN):
        Ele_Array[Row, Col] = int(GmshFile_List[IndexInit_Eles[0]+2+Row][Col])
##===========================
# Remove elements of EleType == 15 and 1.
##---------------------------
# Actually, this script only handles single type of elements in single zone.
# Current method of remaining target type is to remove unnecessary type.
# 15: 1-node point; 1: 2-node line.
EleType15Index = np.where(Ele_Array[:, 1] == 15)[0]
EleType1Index = np.where(Ele_Array[:, 1] == 1)[0]
# Assume elements of type 15 are placed in the first subsection in element section, type 1 in the 2nd.
# So select the max index of elements of type 1 as the index before which we remove.
EleRemoveN = np.max(EleType1Index)+1
EleN = EleN - EleRemoveN
# Get the max number of columns of element: Temp_EleN
# Currently this script only handle single type of elements in single zone.
# Mutiple type of elements, currently select the last element.
Temp_EleN = len(GmshFile_List[IndexEnd_Eles[0]-1])
Ele_Array = np.zeros((EleN, Temp_EleN), dtype=int)
# Read in all nodes
for Row in range(NodeN):
    for Col in range(4):
        Node_Array[Row, Col] = float(GmshFile_List[IndexInit_Nodes[0]+2+Row][Col])
# Only read in elements of type 3 or 2
for Row in range(EleN):
    for Col in range(Temp_EleN):
        Ele_Array[Row, Col] = int(GmshFile_List[IndexInit_Eles[0]+2+EleRemoveN+Row][Col])
# Shift element no to be corrent state
Ele_Array[:, 0] = Ele_Array[:, 0] - EleRemoveN
##---------------------------
###########################################################
# Convert to the face based format
# Extract information from element section
EleN = Ele_Array.shape[0]
EleNo_Array = Ele_Array[:, 0]
EleType = Ele_Array[0, 1]
EleTagN = Ele_Array[0, 2]
##===========================
# Extract face array in terms of element.
##---------------------------
# Extract nodes from element section
# Get node array in terms of element.
EleNode_Array = Ele_Array[:, 2+EleTagN+1:]
# Store Gmsh element type as a list for indexing.
# Column 1 is the number of faces in this element.
# Column 2 is the number of nodes in each face in this element.
EleType_List = [[1, 2], [3, 2], [4, 2]]
EleFaceN = EleType_List[EleType-1][0]
FaceNodeN = EleType_List[EleType-1][1]
# Init face array in terms of element.
EleFace_Array = np.zeros((EleN, EleFaceN, FaceNodeN), dtype=int)
# Roll node array to assist in extracting face array from node array.
EleNodeRoll_Array = np.roll(EleNode_Array, 1, axis=1)
# Extracting face array from node array.
# According to Gmsh Doc, in element section, 2 adjacent nodes make up 1 line in 2D grid.
for EleI in range(EleN):
    for FaceI in range(EleFaceN-1):
        EleFace_Array[EleI, FaceI, :] = EleNode_Array[EleI, FaceI:FaceI+2]
    FaceI = EleFaceN-1
    EleFace_Array[EleI, FaceI, :] = EleNodeRoll_Array[EleI, 0:2]
##---------------------------
##===========================
# Create face array(Face-Based) from face array(Element-Based) 
##---------------------------
# Sort EB face array to be compared to find matched faces.
# Matched faces are the interior faces and should be remove because it's duplicate.
EleFaceSort_Array = np.sort(EleFace_Array)
# Store the 2 elements each face belongs to.
FaceEle2D_Array = np.zeros((EleN*EleFaceN, 2), dtype=int)
# Store the index of interior faces. Incremental append new index.
# After for loops, delete duplicate faces according to this list.
# DO NOT apply delete operation during for loops, because it will mess up the index inside array.
FaceInterior_List = []
for EleI in range(EleN):
    # Assign the first element no current face belongs to.
    FaceEle2D_Array[EleI*EleFaceN:(EleI+1)*EleFaceN, 0] = EleI + 1
    for EleJ in range(EleI+1, EleN):
        # # print 'EleI: ', EleI, '; ', 'EleJ: ', EleJ
        for RollLen in range(1, EleFaceN):
            # Find indices of matched faces
            # Roll an array and then compare the whole array with another.
            MatchIndex_Tuple = np.where( \
                np.all( np.isclose( \
                    EleFaceSort_Array[EleI, :, :], \
                    np.roll(EleFaceSort_Array[EleJ, :, :], \
                    RollLen, axis=0) ), axis=1) )
            # Size != 0 means matched faces. Get the index by MatchIndex and RollLen
            if MatchIndex_Tuple[0].size == 1:
                # Matched faces are EleFaceSort_Array[EleI, MatchIndex[0][0], :] or say EleFaceSort_Array[EleJ, MatchIndex[0][0]-RollLen, :]
                MatchIndex = MatchIndex_Tuple[0][0]
                # Record elements no for current face
                FaceEle2D_Array[EleI*EleFaceN+MatchIndex, 1] = EleJ+1
                # Record the index of duplicate face in Element EleJ
                FaceInterior_List.append(EleJ*EleFaceN+MatchIndex-RollLen)
                break
FaceEle2D_Array = np.delete(FaceEle2D_Array, FaceInterior_List, axis=0)
# Reshape to perform delete operation
EleFace2D_Array = np.reshape(EleFace_Array, (EleN*EleFaceN, FaceNodeN))
EleFace2D_Array = np.delete(EleFace2D_Array, FaceInterior_List, axis=0)
FaceN = FaceEle2D_Array.shape[0]
Face_Array = np.concatenate((np.arange(FaceN, dtype=int).reshape((FaceN,1))+1, np.zeros((FaceN,1), dtype=int)+FaceNodeN, EleFace2D_Array, FaceEle2D_Array), axis=1)
print Face_Array
##---------------------------
###########################################################
# Save as CGNS format


