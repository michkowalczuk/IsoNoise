# -*- coding: utf-8 -*-
import arcpy
import os
import math
import numpy
import model

arcpy.env.overwriteOutput = True
arcpy.env.outputZFlag = "Enabled"

#===============================================================================
# KLASA DATA
#===============================================================================
class Data(object):
    """Klasa przechowująca dane do obliczeń - elemnty modelu"""

    # konstruktor
    def __init__(self, settings):

        # inicjalizowanie list przechowujących obiekty
        self.pointSourceList = [] # źródła punktowe zwykłe i utworzone ze źródeł powierzchniowych
        self.lineSourceList = []
        self.buildingList = []
        self.noiseWallList = []
        self.groundAreaList = []
        self.calcPointList = []
        self.diffractionEdgeList = []

        # calc settings
        self.settings = settings
#         self.groundAreasPath = settings["GEODATABASE"] + "\\groundAreas"
#         self.buildingsPath = settings["GEODATABASE"] + "\\buildings"
#         self.noiseWallsPath = settings["GEODATABASE"] + "\\noiseWalls"

    # WŁASNOŚCI ----------------------------------------------------------------

    @property
    def PointSourcesCount(self):
        return len(self.pointSourceList)

    @property
    def LineSourcesCount(self):
        return len(self.lineSourceList)

    @property
    def BuildingsCount(self):
        return len(self.buildingList)

    @property
    def NoiseWallsCount(self):
        return len(self.noiseWallList)

    @property
    def GroundAreasCount(self):
        return len(self.groundAreaList)

    @property
    def CalcPointsCount(self):
        return len(self.calcPointList)

    @property
    def DiffractionEdgesCount(self):
        return len(self.diffractionEdgeList)

    # METODY -------------------------------------------------------------------

    # dodawanie krawędzi dyfrakcji
    def updateDiffractionEdgeList(self, modelElement, index):
        """
        rozbija poligony lub polilinie elementu wejściowego na obiekty
        'model.Line' i dodaje do listy krawędzi dyfrakcji 'data.diffractionEdgeList'
        
        TO DO:
        dodawanie krawędzi trójkątów triangulacji
        """

        # pobieramy wierzchołki elemtu wejściowego
        if type(modelElement) is model.Building:
            verticesArray = modelElement.Polygon.getPart(0)

        elif type(modelElement) is model.NoiseWall:
            verticesArray = modelElement.Polyline.getPart(0)

        verticesCount = verticesArray.count

        # rozbijanie na odcinki/segmenty
        for iVertex in range(verticesCount - 1):
            startPoint = verticesArray[iVertex]
            endPoint = verticesArray[iVertex + 1]

            if type(modelElement) is model.Building:
                # dla budynków bierzemy średnią elewację
                zStart = zEnd = modelElement.Elevation + modelElement.H

                # typ elementu
                element = 1

            elif type(modelElement) is model.NoiseWall:
                # dla ekranów bierzemy rzeczywistą
                zStart = startPoint.Z + modelElement.H
                zEnd = endPoint.Z + modelElement.H

                # typ elementu
                element = 2

            # tworzenie krawędzi
            edge = model.Edge(arcpy.Point(startPoint.X,
                                          startPoint.Y,
                                          zStart),
                              arcpy.Point(endPoint.X,
                                          endPoint.Y,
                                          zEnd),
                              element, index)

            # aktualizowanie listy krawędzi dyfrakcji
            self.diffractionEdgeList.append(edge)

    # dodawanie źródeł punktowych
    def addPointSources(self, pointSourcesPath):
        with arcpy.da.SearchCursor(pointSourcesPath, ("OID@", "SHAPE@", "HEIGHT", "LWA", "DI", "REF_PLANES")) as cursor:
            for row in cursor:
                pointSource = model.PointSource(row[1], # SHAPE (POINTGEOMETRY)
                                                row[2], # HEIGHT
                                                row[3], # LWA
                                                row[4], # DI
                                                row[5]) # REF_PLANES
                self.pointSourceList.append(pointSource)

    # dodawanie źródeł liniowych
    def addLineSources(self, lineSourcesPath):
        with arcpy.da.SearchCursor(lineSourcesPath, ("OID@", "SHAPE@", "HEIGHT", "LWA", "LWA_TYPE", "V_KM_H", "N")) as cursor:
            for row in cursor:
                lineSource = model.LineSource(row[1], # SHAPE (POLYLINE)
                                              row[2], # HEIGHT
                                              row[3], # LWA
                                              row[4], # LWA_TYPE
                                              row[5], # V_KM_H
                                              row[6]) # N

                self.lineSourceList.append(lineSource)

    # dodawanie źródeł powierzchniowych
    def addAreaSources(self, areaSourcesPath):
        with arcpy.da.SearchCursor(areaSourcesPath, ("OID@", "SHAPE@", "HEIGHT", "LWA", "LWA_TYPE")) as cursor:
            for row in cursor:
                areaSource = model.AreaSource(row[1], # SHAPE (POLYGON)
                                              row[2], # HEIGHT
                                              row[3], # LWA
                                              row[4]) # LWA_TYPE

                pointSources = areaSource.toPointSources(self.settings["STEP_AREASOURCE"])
                self.pointSourceList.extend(pointSources)

    # dodawanie budynków
    def addBuildings(self, buildingsPath):

        index = 0
        with arcpy.da.SearchCursor(buildingsPath, ("OID@", "SHAPE@", "H")) as cursor:
            for row in cursor:
                building = model.Building(row[1], # SHAPE (POLYGON)
                                          row[2]) # H

                self.buildingList.append(building)

                # rozbijanie budynków na krawędzie dyfrakcji
                self.updateDiffractionEdgeList(building, index)

                index += 1

    # dodawanie ekranów
    def addNoiseWalls(self, noiseWallsPath):

        index = 0
        with arcpy.da.SearchCursor(noiseWallsPath, ("OID@", "SHAPE@", "H", "DL_ALFA")) as cursor:
            for row in cursor:
                noiseWall = model.NoiseWall(row[1], # SHAPE (POLYLINE)
                                            row[2], # H
                                            row[3]) # DL_ALFA

                self.noiseWallList.append(noiseWall)

                # rozbijanie ekranów na krawędzie dyfrakcji
                self.updateDiffractionEdgeList(noiseWall, index)

                index += 1

    # dodawanie gruntów
    def addGroundAreas(self, groundAreasPath):

        with arcpy.da.SearchCursor(groundAreasPath, ("OID@", "SHAPE@", "G")) as cursor:
            for row in cursor:
                groundArea = model.GroundArea(row[1], # SHAPE (POLYGON)
                                              row[2]) # G

                self.groundAreaList.append(groundArea)

    # dodawanie punktów imisji
    def addReceivers(self, receiversPath):

        # przed dodaniem punktów trzeba usunąć te leżące wewnątrz budynków
        # wymagane jest, aby najpierw załadować budynki do modelu
        if self.BuildingsCount:
            buildingsPath = self.settings["GEODATABASE"] + "\\Buildings"
            receiversOkPath = r"in_memory\receiversOk"

            if arcpy.CheckProduct("ArcInfo") == "Available":
                arcpy.Erase_analysis(receiversPath, buildingsPath, receiversOkPath)

            else:
                # TO DO: obsłużyć 'Erase' w przypadku niższej licencji
                # praktycznie zrobione - jeszcze nie przeszło testów
                receiversMemoryPath = r"in_memory\receivers"
                buildingsMemoryPath = r"in_memory\buildings"
                arcpy.CopyFeatures_management(receiversPath, receiversMemoryPath)
                arcpy.CopyFeatures_management(buildingsPath, buildingsMemoryPath)

                # Process: Make Feature Layer
                receiversLayer = r"receiversLayer"
                arcpy.MakeFeatureLayer_management(receiversMemoryPath, receiversLayer, "", "", "")

                # Process: Select Layer By Location
                arcpy.SelectLayerByLocation_management(receiversLayer, "INTERSECT", buildingsMemoryPath, "", "NEW_SELECTION")

                # Process: Select Layer By Attribute
                arcpy.SelectLayerByAttribute_management(receiversLayer, "SWITCH_SELECTION", "")

                # Process: Copy Features
                arcpy.CopyFeatures_management(receiversLayer, receiversOkPath, "", "0", "0", "0")
        else:
            receiversOkPath = receiversPath

        with arcpy.da.SearchCursor(receiversOkPath, ("OID@", "SHAPE@", "HEIGHT")) as cursor:
            for row in cursor:
                receiver = model.Receiver(row[1], # SHAPE (POLYGON)
                                          row[2]) # HEIGHT

                self.calcPointList.append(receiver)

    # dodawanie obszaru obliczeń (siatki)
    def addCalcAreas(self, calcAreasPath):

        # przed dodaniem obszaru trzeba wyciąc z nich budynki
        # wymagane jest, aby najpierw załadować budynki do modelu
        if self.BuildingsCount:

            buildingsPath = self.settings["GEODATABASE"] + "\\Buildings"
            calcAreasOkPath = r"in_memory\calcAreasOk"

            if arcpy.CheckProduct("ArcInfo") == "Available":
                arcpy.Erase_analysis(calcAreasPath, buildingsPath, calcAreasOkPath)

            else:
                # TO DO: obsłużyć 'Erase' w przypadku niższej licencji
                # praktycznie zrobione - przeszło testy
                calcAreasMemoryPath = r"in_memory\calcAreas"
                buildingsMemoryPath = r"in_memory\buildings"
                arcpy.CopyFeatures_management(calcAreasPath, calcAreasMemoryPath)
                arcpy.CopyFeatures_management(buildingsPath, buildingsMemoryPath)

                # Process: Clip
                clipMemoryPath = r"in_memory\clip"
                arcpy.Clip_analysis(calcAreasMemoryPath, buildingsMemoryPath, clipMemoryPath, "")

                # Process: Union
                unionMemoryPath = r"in_memory\union"
                arcpy.Union_analysis([clipMemoryPath, calcAreasMemoryPath], unionMemoryPath, "ALL", "", "GAPS")

                # Process: Make Feature Layer
                unionLayer = r"unionLayer"
                arcpy.MakeFeatureLayer_management(unionMemoryPath, unionLayer, "", "", "")

                # Process: Select Layer By Location
                arcpy.SelectLayerByLocation_management(unionLayer, "ARE_IDENTICAL_TO", clipMemoryPath, "", "NEW_SELECTION")

                # Process: Select Layer By Attribute
                arcpy.SelectLayerByAttribute_management(unionLayer, "SWITCH_SELECTION", "")

                # Process: Copy Features
                arcpy.CopyFeatures_management(unionLayer, calcAreasOkPath, "", "0", "0", "0")

        else:
            calcAreasOkPath = calcAreasPath

        with arcpy.da.SearchCursor(calcAreasOkPath, ("OID@", "SHAPE@", "HEIGHT")) as cursor:
            for row in cursor:
                calcArea = model.CalcArea(row[1], # SHAPE (POLYGON)
                                          row[2]) # HEIGHT

                gridPoints = calcArea.makeGrid(self.settings["SPACING_CALC"])

                self.calcPointList.extend(gridPoints)

#===============================================================================
# KLASA DIFFRACTION DATA
#===============================================================================
class DiffractionData(object):
    def __init__(self):
        self._diffractionPoints = []
        self._differencePaths = []

        # wszystkie krawędzie przecinające prostą RS
        # tupla (element, index)
        self._elements = []

    def addPoint(self, point, pathDifference, diffractionType=1):
        """ Dodaje punkt dyfrakcyjny"""

        if not self._diffractionPoints:
            # pusta lista zwraca 'False'
            self._diffractionPoints.append(point)
            self._differencePaths.append(pathDifference)

        elif len(self._diffractionPoints) == 1:
            if not point.equals(self._diffractionPoints[0]):

                if diffractionType == 2:
                    if (abs(pathDifference) < 0.001 or
                        abs(self._differencePaths[0]) < 0.001):
                        # diffractionType=2 tylko dla dyfrakcji na krawędzi bocznej
                        # dozwolony tylko jeden punkt leżący na ścieżce RS
                        self._diffractionPoints.remove(self._diffractionPoints[0])
                        self._differencePaths.remove(self._differencePaths[0])
                        self._diffractionPoints.append(point)
                        self._differencePaths.append(pathDifference)
                else:
                    self._diffractionPoints.append(point)
                    self._differencePaths.append(pathDifference)

        else:
            if (not point.equals(self._diffractionPoints[0])) and (not point.equals(self._diffractionPoints[1])):
                if self._differencePaths[0] > self._differencePaths[1]:
                    if pathDifference > self._differencePaths[0]:
                        self._diffractionPoints[0] = point
                        self._differencePaths[0] = pathDifference

                    elif pathDifference > self._differencePaths[1]:
                        self._diffractionPoints[1]= point
                        self._differencePaths[1] = pathDifference

                else:
                    if pathDifference > self._differencePaths[1]:
                        self._diffractionPoints[1]= point
                        self._differencePaths[1] = pathDifference

                    elif pathDifference > self._differencePaths[0]:
                        self._diffractionPoints[0]= point
                        self._differencePaths[0] = pathDifference

    def addElement(self, element, index):
        """ Dodaje tuple z informacją o typie elementu i jego indeksie
        1 - budynek
        2 - ekran
        """
        elementTuple = (element, index)
        if self._elements.count(elementTuple) == 0:
            self._elements.append(elementTuple)

    @property
    def DiffractionPoints(self):
        return self._diffractionPoints

    @property
    def Elements(self):
        return self._elements

    @property
    def Count(self):
        return len(self._diffractionPoints)

    @property
    def Type(self):
        if self.Count == 0:
            return "NONE"
        elif self.Count == 1:
            return "SINGLE"
        elif self.Count == 2:
            return "DOUBLE"

#===============================================================================
# FUNKCJA ATKOSPHERIC ATTEUNATION
#===============================================================================
def atmosphericAttenuation(temperature, humidity, atmosphericPressure, octaveBand=500):

    """
    This class compute sound atmospheric attenuation for octave band
    INPUT DATA:
    * temperature [oC]
    * humidity [%]
    * atmosphericPressure [kPa]
    """

    # ciśnienie atmosferyczne odniesienia, w kPa
    # - reference pressure of one standard atmosphere
    pr = 101.325

    # temperatura odniesienia powietrza, w Kelwinach
    # - reference ambient temperature
    To = 293.15 # = 20oC

    # temperatura punktu potrójnego izotermy, w Kelwinach
    # - triple-point isotherm temperature
    T01 = 273.16

    # T - temp. powietrza, w Kelwinach
    # - ambient atmospheric temperature
    T = temperature + 273.15

    # ciśnienie atmosfery ziemskiej, w kPa
    # - ambient atmospheric pressure
    pa = atmosphericPressure

    # wilgotność względna, w %
    # relative humidity
    hr = humidity

    # pa/pr
    pa_pr = pa / pr

    # T/To
    T_To = T / To

    # T01/T
    T01_T = T01 / T

    # zmienna pomocnicza C
    C = -6.8346 * math.pow(T01_T, 1.261) + 4.6151

    # ciśnienie pary nasyconej
    # - saturation pressure
    psat = pr * math.pow(10, C)

    # molowe stężenie pary wodnej, w %
    # - molar concentration of water vapor
    h = hr * psat / pa

    # częstotliwość relaksacyjna tlenu
    frO = pa_pr * (24 + 4.04 * 10000 * h * (0.02 + h) / (0.391 + h))

    # częstotliwość relaksacyjna azotu
    frN = pa_pr * math.pow(T_To, -0.5) * (9 + 280 * h * math.exp(-4.170 * (math.pow(T_To, -1.0 / 3.0) - 1)))

    # część wzoru na alfa niezależna od częstotliwości
    a = 1.84 * 0.00000000001 / pa_pr * math.sqrt(T_To)

    # część zależna od częstotliwości
    # część związana z frO
    afrO = 0.01275 * math.exp(-2239.1 / T) / (frO + math.pow(octaveBand, 2) / frO)

    # część związana z frN
    afrN = 0.1068 * math.exp(-3352 / T) / (frN + math.pow(octaveBand, 2) / frN);

    # współczynnik tłumienia spowodowanego pochłanianiem przez atmosferę, w dB/m
    alpha = 8.686 * math.pow(octaveBand, 2) * (a + math.pow(T_To, -2.5) * (afrO + afrN));

    return alpha

#===============================================================================
# METHOD CALCG
#===============================================================================
def calcG(regionLine, dRegion, groundAreaList, defaultG):
    """
    """

    G = 0.0
    dIntersect = 0.0

    # pętla po obszarach pokrycia terenu
    for groundArea in groundAreaList:

        if regionLine.Polyline.disjoint(groundArea.Polygon):
            # brak przecięć ścieżki z obszarami
            continue

        else:
            # wynikiem multipart polyline
            regionLineIntersectLine = regionLine.Polyline.intersect(groundArea.Polygon, 2)

            gSegment = groundArea.G

            # pętla po liniach przecięcia ścieżki z obszarami tłumienia
            # w strefie źródła
            for iPart in range(regionLineIntersectLine.partCount):
                iRegionLineIntersectLine = arcpy.Polyline(regionLineIntersectLine.getPart(iPart))
                dSegment = iRegionLineIntersectLine.length

                dIntersect += dSegment
                G += gSegment * dSegment / dRegion

    # na koniec uwzlgędnienie obszarów bez pokrycia
    G += defaultG * (dRegion- dIntersect) / dRegion

    return G

#===============================================================================
# METHOD CALCABAR
#===============================================================================
def calcAbar(lineRS, diffractionData, settings, waveLength, d, C2, Agr, barrierType):
    if diffractionData.Type == "NONE":
        # brak ekranowania
        Abar = 0

    else:
        if diffractionData.Type == "SINGLE":
            # ugięcie pojedyncze
            AbarMax = settings["MAX_ABAR_SINGLE_CALC"]

            C3 = 1
            dsr, e, dss = lineRS.diffrationPathSegments(diffractionData.DiffractionPoints[0])

        elif diffractionData.Type == "DOUBLE":
            # ugięcie podwójne lub wyższe
            AbarMax = settings["MAX_ABAR_DOUBLE_CALC"]

            dsr, e, dss = lineRS.diffrationPathSegments(diffractionData.DiffractionPoints[0],
                                                        diffractionData.DiffractionPoints[1])

            # wzór 15. normy
            C3 = (1 + (5*waveLength/e)**2) / (1/3 + (5*waveLength/e)**2)

        # obliczanie różnicy dróg propagacji - wzór 17. normy
        z = dsr + e + dss - d

        # poprawka meteorologiczna 'Kmet' zgodnie z wzorem 18. normy
        if z > 0:
            Kmet = math.exp(-0.0005 * math.sqrt(dss * dsr * d / (2 * z)))
        else:
            Kmet = 1

        # część równania na 'Dz' pod logarytmem musi być większa od zera
        DzLgEquation = 3 + C2 / waveLength * C3 * z * Kmet

        if DzLgEquation <= 0:
            Dz = -999
        else:
            Dz = 10 * math.log10(DzLgEquation)

        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        # Abar - tłumienie wtrącenia
        #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
        if settings["ALTERNATIVE_ABAR_CALC"]:
            if Agr < 0:
                Agr = 0

        if barrierType == "TOP":
            if Dz < Agr:
                Abar = 0
            else:
                Abar = Dz - Agr
        elif barrierType == "VERTICAL":
            if Dz > 0:
                Abar = Dz
            else:
                Abar = 0
        if Abar > AbarMax:
            Abar = AbarMax

    return Abar

#===============================================================================
# METHOD CALCABARSIDE
#===============================================================================
def calcAbarSide(sideVerticesArray, lineRS, sideDiffractionData, settings, waveLength, d, C2, Agr):

    # tworzenie obiektu 'arcpy.Multipoint' w celu wyznaczenia
    # otoczki punktów (convex hull)
    sideMultipoint = arcpy.Multipoint(sideVerticesArray, None, True)
    sideConvexHull = sideMultipoint.convexHull()

    if sideConvexHull.type != 'polyline':
        sideDiffractionVertices = sideConvexHull.getPart(0)
    else:
        sideDiffractionVertices = sideVerticesArray

    for sideVertex in sideDiffractionVertices:
        if not (sideVertex.equals(sideVerticesArray[0]) or
                sideVertex.equals(sideVerticesArray[1])):

            # różnica dróg propagacji
            pathDifference = lineRS.pathDifference(sideVertex)

            # dodawanie informacji o punkcie dyfrakcji do obiektu
            # 'topDiffractionData'
            sideDiffractionData.addPoint(sideVertex, pathDifference, 2)

    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Abar  - obliczanie ekranowania na krawędzi górnej
    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    AbarSide = calcAbar(lineRS, sideDiffractionData, settings, waveLength, d, C2, Agr, "VERTICAL")

    return AbarSide


#===============================================================================
# METHOD RUN
#===============================================================================
"""
 LfT(DW) = LW + DC - A
 
 DC = DI + DΩ (directivity correction)
 
 A = Adiv + Aatm + Agr + Abar + Amisc
 
 Adiv is the attenuation due to geometrical divergence (see 7.1);
 Aatm(f) is the attenuation due to atmospheric absorption (see 7.2);
 Agr(f) is the attenuation due to the ground effect (see 7.3);
 Abar(f) is the attenuation due to a barrier (see 7.4);
 Amisc is the attenuation due to miscellaneous other effects (see annex A).
 
 NOTE 1 If only A-weighted sound power levels of the sources are known,
 the attenuation terms for 500 Hz may be used to estimate the resulting attenuation.
 """

def run(data):

    calcPointsCount = len(data.calcPointList)

    # PROGRESS BAR
    arcpy.SetProgressor("step", "Obliczenia...", 0, calcPointsCount, 1)

    resultFile = open(os.path.join(data.settings["RESULTS_FOLDER"], "results.txt"), 'w')
    resultFile.write("X\tY\tLDW\n")

    # tablica z wynikami: (1)'X', (2)'Y', (3)'Z', (4)'LDW'

    ## # w wersji 'DETAILED': (5)'DI', (6)'DO' (5)'Adiv', (6)'Aatm', (7)'Agr', (8)'Abar', (9)'AbarVert1', (10)'AbarVert2'

    resultArray = numpy.zeros((calcPointsCount, 1), dtype=[('X',numpy.float32),
                                                           ('Y',numpy.float32),
                                                           ('Z',numpy.float32),
                                                           ('LDW',numpy.float32)])

# # #     if data.settings["DETAILED_RESULTS"]:
# # #         #tu tablica w wersji detailed


    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # ustalanie danych niezależnych od położenia źródeł/punktów imisji
    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    # wyznaczanie prędkości dźwięku
    c = 331.5 * math.sqrt(1 + data.settings["TEMPERATURE"] / 273.15)

    # długość fali dla 500 Hz
    lambda500Hz = c / 500

    # parametr C2 uwzględniający wpływ odbić od gruntu - wzór 14. normy
    # jeżeli odbicie od gruntu uwzględnia się w postaci źródeł pozornych
    # to C2 = 40
    C2 = 20

    # wyznaczanie współczynnika pochłaniania atmosferycznego
    # na podstawie ISO 9613-1 (tylko dla 500 Hz - rozdz. 1, UWAGA 1)
    alfa = atmosphericAttenuation(data.settings["TEMPERATURE"],
                                data.settings["HUMIDITY"],
                                data.settings["ATMOSPHERIC_PRESSURE"] / 10,
                                500)

    minStep = data.settings["MIN_STEP_LINESOURCE"]
    ratio = data.settings["DHMAX_RATIO_LINESOURCE"]

    # iterator
    iCalcPoint = -1

    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # obliczenia właściwe
    #:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    # pętla po wszystkich punktach obliczeniowych
    for calcPoint in data.calcPointList:

        # zaczynamy iterować od indeksu 0
        iCalcPoint += 1

        ### PROGRESS BAR
        arcpy.SetProgressorPosition()
        arcpy.SetProgressorLabel("Calculation point: {0}/{1}".format(iCalcPoint + 1, calcPointsCount))

#         print "calc point: {0} / {1}".format(iCalcPoint+1, calcPointsCount)

        # lista dla wartości poziomu od każdego źródła
        LDWList = []

        # wysokość receptora nad powierzchnią gruntu (Agr)
        hr = calcPoint.Height

        #-----------------------------------------------------------------------
        # dzielenie źródeł liniowych na segmenty
        # i tworzenie zastępczych źródeł punktowych
        #-----------------------------------------------------------------------

        # dla każdego punktu obliczeniowego będzie inny zestaw źródeł punktowych
        # baza ta sama, zmieniać się będą te utworzone ze źródeł liniowych
        pointSourceFromLineSourceList = []

        # pętla po źródłach liniowych
        for lineSource in data.lineSourceList:

            # lista wierzchołków źródła liniowego
            lineSourceVertices = lineSource.Polyline.getPart(0)

            # pętla po wierzchołkach (tak naprawdę segmantach)
            for iVertex in range(lineSourceVertices.count - 1):

                # tworzony obiekt 'Line' na podstawie rzeczywistej współzędnej Z
                line = model.Line(lineSourceVertices[iVertex],
                                  lineSourceVertices[iVertex + 1],
                                  lineSource.Height)

                # minimalna odległość segmentu od punktu obliczeniowego
                minDistanceToSegment = line.minimumDistanceToPoint3D(calcPoint.Point)

                # długość segmentu źródła musi być odpowiednio mniejsza
                # od odległości D (rozdz. 4.c: D/Hmax > ratio)
                # tu wyznaczam wartość graniczną
                segmentLength = minDistanceToSegment / ratio

                if segmentLength < minStep:
                    # przyjmujemy minimalny krok podziału
                    segmentLength = minStep

                # dzielenie obiektu na segmenty o zadanej długości
                segmentList = line.divide(segmentLength)

                # pętla po segmentach
                for segment in segmentList:

                    # środek segmentu
                    centrePointReal = segment.CentrePoint3D
                    centrePoint = centrePointReal
                    centrePoint.Z -= lineSource.Height

# # #                     # odległość (3D) punktu obliczeniowego od prostej
# # #                     # utworzonej przez segment źróła liniowego
# # #                     d = segment.distanceToPoint3D(calcPoint.Point)
# # #                     print segment.Length3D

                    # do określenia poziomu mocy źródła zastępczego wystarczy długość segmentu
                    lwaPrim = lineSource.getLWA(segment.Length3D)


                    # tworzenie źródła punktowego w środku segmentu
                    pointSourceFromSegment = model.PointSource(arcpy.PointGeometry(centrePoint, None, True),
                                                               lineSource.Height,
                                                               lwaPrim,
                                                               name=lineSource.Name)

                    pointSourceFromLineSourceList.append(pointSourceFromSegment)

        # zbiór źródeł punktowych dla aktualnego punktu imisji
        currentPointSourceList = data.pointSourceList + pointSourceFromLineSourceList
        #-----------------------------------------------------------------------
        # obliczenia tłumienia od każdego źródła punktowego
        #-----------------------------------------------------------------------
# # #         iS = 0
# # #         nS = len(currentPointSourceList)
# # #         print "sources: {0}".format(nS)
        for pointSource in currentPointSourceList:

###            iS += 1
###            print "source: {0} / {1}".format(iS, nS)

            # source elevation (Agr)
            hs = pointSource.Height

            # tworzymy odcinek punkt imisji - źródło
            lineRS = model.Line(calcPoint.Point, pointSource.Point)
            d = lineRS.Length3D
            dp = lineRS.Length

            if d > data.settings["MAX_RADIUS_CALC"]:
                # źródło poza okręgiem przeszukiwania
                continue

            #-------------------------------------------------------------------
            # Adiv - rozbieżność geometryczna
            #-------------------------------------------------------------------
            Adiv = 20 * math.log10(d) + 11

            #-------------------------------------------------------------------
            # Aatm - pochłanianie przez atmosferę
            #-------------------------------------------------------------------
            # ISO 9613-1 daje wynik w dB/m, więc nie dzielimy przez 1000
            Aatm = d * alfa

            #-------------------------------------------------------------------
            # wpływ gruntu (tylko dla 500 Hz)
            #-------------------------------------------------------------------
            if data.settings["ALTERNATIVE_AGR_CALC"] == False:

                #---------------------------------------------------------------
                # As - strefa źródła
                #---------------------------------------------------------------
                if hs == 0:
                    # brak strefy źródła
                    As = 0
                    # do użycia w strefie środkowej
                    sourceRegionEndPoint = lineRS.EndPoint

                else:
                    # długość strefy źródła = 30 * hs
                    if 30 * hs > dp:
                        dSourceRegion = dp
                        sourceRegionLine = lineRS
                        sourceRegionEndPoint = lineRS.StartPoint
                    else:
                        # tworzenie ścieżki w obrębie strefy źródła
                        dSourceRegion = 30 * hs
                        sourceRegionEndPoint = lineRS.pointAlong(dSourceRegion, "from_end")
                        sourceRegionLine = model.Line(lineRS.EndPoint,
                                                      sourceRegionEndPoint,
                                                      dimension=2)

                    # obliczanie średnio-ważonego wsółczynnika G
                    Gs = calcG(sourceRegionLine, dSourceRegion,
                               data.groundAreaList, data.settings["G_GROUNDAREA"])

                    # obliczanie współczynnika c'(h) - Tablica 3. z normy
                    cPrimHs = 1.5 + 14 * math.exp(-0.46 * hs ** 2) * (1 - math.exp(-dp / 50))

                    # tłumienie strefy źródła
                    As = -1.5 + Gs * cPrimHs

                #---------------------------------------------------------------
                # Ar - strefa odbiorcy
                #---------------------------------------------------------------
                if hr == 0:
                    # brak strefy odbiorcy
                    Ar = 0
                    # do użycia w strefie środkowej
                    receiverRegionEndPoint = lineRS.StartPoint

                else:
                    # długość strefy odbiorcy = 30 * hr
                    if 30 * hs > dp:
                        dReceiverRegion = dp
                        receiverRegionLine = lineRS
                        receiverRegionEndPoint = lineRS.EndPoint
                    else:
                        # tworzenie ścieżki w obrębie strefy źródła
                        dReceiverRegion = 30 * hr
                        receiverRegionEndPoint = lineRS.pointAlong(dReceiverRegion, "from_start")
                        receiverRegionLine = model.Line(lineRS.StartPoint,
                                                        receiverRegionEndPoint,
                                                        dimension=2)

                    # obliczanie średnio-ważonego wsółczynnika G
                    Gr = calcG(receiverRegionLine, dReceiverRegion,
                               data.groundAreaList, data.settings["G_GROUNDAREA"])

                    # obliczanie współczynnika c'(h) - Tablica 3. z normy
                    cPrimHr = 1.5 + 14 * math.exp(-0.46 * hr ** 2) * (1 - math.exp(-dp / 50))

                    # tłumienie strefy odbiorcy
                    Ar = -1.5 + Gr * cPrimHr

                #---------------------------------------------------------------
                # Am - strefa środkowa
                #---------------------------------------------------------------
                if dp <= 30 * (hs + hr):
                    # brak strefy środkowej (norma 7.3.1.c)
                    Am = 0

                else:
                    # długość strefy środkowej
                    dMiddleRegion = dp - 30 * (hs + hr)

                    # tworzenie ścieżki w obrębie strefy środkowej
                    middleRegionStartPoint = sourceRegionEndPoint
                    middleRegionEndPoint = receiverRegionEndPoint

                    middleRegionLine = model.Line(middleRegionStartPoint,
                                                  middleRegionEndPoint,
                                                  dimension=2)

                    # obliczanie średnio-ważonego wsółczynnika G
                    Gm = calcG(middleRegionLine, dMiddleRegion,
                               data.groundAreaList, data.settings["G_GROUNDAREA"])

                    # obliczanie współczynnika q - Tablica 3. normy
                    q = 1 - 30 * (hs + hr) / dp

                    # tłumienie strefy środkowej
                    Am = -3 * q * (1 - Gm)

                #---------------------------------------------------------------
                # Agr - całkowite tłumienie przez grunt
                #---------------------------------------------------------------
                Agr = As + Am + Ar

            else:
                #---------------------------------------------------------------
                # Alternatywna metoda obliczania tłumienia dźwięku (norma 7.3.2)
                #---------------------------------------------------------------
                # do pełnego zaimplementowania wymagany rozszerzenie '3D'
                # można rozpatrzyć wykorzystanie w płaskim terenie
                # gdy dźwięk rozchodzi się nad terenem głównie porowatym
                hm = (hs + hr) / 2
                Agr = 4.8 - 2 * hm / d * (17 + 300 / d)
                if Agr < 0:
                    Agr = 0

                # Directivity Omega (alternatywne)
                DOAlternative = 10 * math.log10(1 + d**2 / (dp**2 +(hs+hr)**2))

            #-------------------------------------------------------------------
            # Ekranowanie na krawędzi górnej
            #-------------------------------------------------------------------
            # obiekt do zbierania informacji o dyfrakcji
            topDiffractionData = DiffractionData()

            # petla po wszystkich krawędziach dyfrakcyjnych
            for iEdge in range(data.DiffractionEdgesCount):

                diffractionEdge = data.diffractionEdgeList[iEdge]
                if lineRS.Polyline.disjoint(diffractionEdge.Polyline):
                    # brak przecięć ścieżki z budynkami
                    continue

                else:
                    # dodawanie indformacji o elemencie biorącym udział w dyfrakcji
                    topDiffractionData.addElement(diffractionEdge.Element, diffractionEdge.Index)

                    # wyznaczanie punktów przecięcia
                    intersectMultipoint = lineRS.Polyline.intersect(diffractionEdge.Polyline, 1)

                    for intersectPoint in intersectMultipoint:

                        """
                        jednak rezygnuję z tego warunku, bo w niektórych
                        przypadkach nie uwzględniona zostanie dyfrakcja
                        na krawędzi bocznej
                        # nie bierzemy pod uwagę punktów dyfrakcyjnych leżących
                        # idealnie na wierzchołku bariery
                        if (model.pointDistance(intersectPoint, diffractionEdge.StartPoint) < 0.0001 or
                            model.pointDistance(intersectPoint, diffractionEdge.EndPoint)  < 0.0001):
                            continue
                        """

                        # współrzędna Z wzdłuż odcinka RS w miejscu bariery
                        zAlongLineRS = lineRS.getZAlong(intersectPoint.X, intersectPoint.Y)

                        # współrzędna Z krawędzi dyfrakcji
                        zDiffractionPoint = diffractionEdge.getZAlong(intersectPoint.X, intersectPoint.Y)

                        # punkt dyfrakcyjny
                        diffractionPoint = arcpy.Point(intersectPoint.X,
                                                       intersectPoint.Y,
                                                       zDiffractionPoint)

                        # różnica dróg propagacji
                        pathDifference = lineRS.pathDifference(diffractionPoint)

                        # jeżeli obserwator widzi źródło to różnica dróg
                        # propagacji przyjmuje wartością ujemną
                        if  zDiffractionPoint < zAlongLineRS:
                            pathDifference = -pathDifference

                        # dodawanie informacji o punkcie dyfrakcji do obiektu
                        # 'topDiffractionData'
                        topDiffractionData.addPoint(diffractionPoint, pathDifference)

            #-------------------------------------------------------------------
            # Abar  - obliczanie ekranowania na krawędzi górnej
            #-------------------------------------------------------------------
            Abar = calcAbar(lineRS, topDiffractionData, data.settings, lambda500Hz, d, C2, Agr, "TOP")

            #-------------------------------------------------------------------
            # Ekranowanie na krawędziach bocznych
            #-------------------------------------------------------------------
            if data.settings["SIDE_DIFFRACTION_CALC"]:

                # obiekty do zbierania informacji o dyfrakcji
                upSideDiffractionData = DiffractionData()
                downSideDiffractionData = DiffractionData()

                if topDiffractionData.Type == "NONE":
                    # brak ekranowania w ogóle
                    AbarUpSide = 0
                    AbarDownSide = 0

                else:
                    # analizujemy wszystkie elementy modelu, które brały udział
                    # w dyfrakcji górnej
                    # - tworzymy listę punktów z wierzchołków tych obiektów
                    vertices = arcpy.Array()

                    for element in topDiffractionData.Elements:
                        elementType = element[0]
                        index = element[1]

                        if elementType == 1:
                            # budynek
                            buildingVertices = data.buildingList[index].VerticesArray
                            vertices.extend(buildingVertices)

                        elif elementType == 2:
                            # ekran
                            noiseWallVertices = data.noiseWallList[index].VerticesArray
                            vertices.extend(noiseWallVertices)

                    # sprawdzamy każdy wierzchołek takiej krawędzie i umieszczamy go
                    # do odpowiedniego zbioru - nad lub pod prostą RS
                    # pod warunkiem, że dyfrakcja nastąpi
                    upSideVerticesArray = arcpy.Array([calcPoint.Point, pointSource.Point])
                    downSideVerticesArray = arcpy.Array([calcPoint.Point, pointSource.Point])

                    for vertex in vertices:

                        # sprawdzanie, po której stronie ścieżki RS
                        # w płaszczyźnie XY znanduje się punkt
                        side = lineRS.side(vertex.X, vertex.Y)

                        # współrzędne punktu na ścieżce RS, w miejscu przecięcia
                        # jej z prostą prostopadłą przechodzącą przez punkt 'Vertex'
                        xAlongLineRS, yAlongLineRS = lineRS.getXYAlongFromNearPoint(vertex)

                        # zastosowane uproszczenie:
                        # uwzględniane są punkty dyfrakcyjne pomiędzy odbiornikiem
                        # a źródłem, tak więc jęzeli przegroda otacza częściowo
                        # odbiornik lub źródło - dyfrakcja jest pomijana
                        # można założyć, że w takich przyoadkach spadek poziomu
                        # jest tak duży, że nie wnosiłby nic do poziomu wypadkowego

                        # zmienna 't' równania parametrycznego prostej wzdłuż ścieżki RS
                        tAlongLineRS = lineRS.getTAlong(xAlongLineRS, yAlongLineRS)

                        if 0 <= tAlongLineRS <= 1:
                            # parametr 't' jest w zakresie ścieżki 'lineRS'

                            # obliczanie współrzędnej 'Z' punktu dyfrakcyjnego
                            zDiffraction = lineRS.getZAlong(xAlongLineRS, yAlongLineRS)

                        else:
                            # punkt dyfrakcyjny jest przed lub za ścieżką
                            # (t<0 lub t>1) - inny sposób obliczania wsp. 'Z'
                            # punktu dyfrakcyjnego - coś w stylu źródła pozornego
                            # wyznaczam długości dwóch ścieżek
                            dRVertex = model.pointDistance(lineRS.StartPoint, vertex)
                            dVertexS = model.pointDistance(vertex, lineRS.EndPoint)

                            # określam ekwiwalentny parametr 't'
                            tRVertex = dRVertex / (dRVertex + dVertexS)

                            # na jego podstawie określam 'Z' punktu dyfrakcyjnego
                            zDiffraction = lineRS.Z1 + lineRS.R * tRVertex

                        if vertex.Z >= zDiffraction:
                            # dyfrakcja nastąpi - punkt nie jest za nisko

                            vertex.Z = zDiffraction

                            if side > 0:
                                upSideVerticesArray.append(vertex)

                            elif side < 0:
                                downSideVerticesArray.append(vertex)

                            else:
                                # testowa wersja
                                # wierzchołek leżący na linii RS dodawany jest
                                # do obu zbiorów, będzie on odfiltrowywany
                                # później w diffractionData
                                upSideVerticesArray.append(vertex)
                                downSideVerticesArray.append(vertex)

                    AbarUpSide = calcAbarSide(upSideVerticesArray, lineRS, upSideDiffractionData, data.settings, lambda500Hz, d, C2, Agr)
                    AbarDownSide = calcAbarSide(downSideVerticesArray, lineRS, downSideDiffractionData, data.settings, lambda500Hz, d, C2, Agr)


# # #                     # tworzenie obiektu 'arcpy.Multipoint' w celu wyznaczenia
# # #                     # otoczki punktów (convex hull)
# # #                     upSideMultipoint = arcpy.Multipoint(upSideVerticesArray, None, True)
# # #                     downSideMultipoint = arcpy.Multipoint(downSideVerticesArray, None, True)
# # #
# # #                     upSideConvexHull = upSideMultipoint.convexHull()
# # #                     downSideConvexHull = downSideMultipoint.convexHull()
# # #
# # #                     if upSideConvexHull.type != 'polyline':
# # #                         verticesToIterate = upSideConvexHull.getPart(0)
# # #                     else:
# # #                         verticesToIterate = upSideVerticesArray
# # #
# # #                     for upSideVertex in verticesToIterate:
# # #                         if not (upSideVertex.equals(calcPoint.Point) or
# # #                                 upSideVertex.equals(pointSource.Point)):
# # #
# # #                             # różnica dróg propagacji
# # #                             pathDifference = lineRS.pathDifference(upSideVertex)
# # #
# # #                             # dodawanie informacji o punkcie dyfrakcji do obiektu
# # #                             # 'topDiffractionData'
# # #                             upSideDiffractionData.addPoint(upSideVertex, pathDifference, 2)
# # #
# # #                     if downSideConvexHull.type != 'polyline':
# # #                         verticesToIterate = downSideConvexHull.getPart(0)
# # #                     else:
# # #                         verticesToIterate = downSideVerticesArray
# # #
# # #                     for downSideVertex in verticesToIterate:
# # #                         if not (downSideVertex.equals(calcPoint.Point) or
# # #                                 downSideVertex.equals(pointSource.Point)):
# # #
# # #                             # różnica dróg propagacji
# # #                             pathDifference = lineRS.pathDifference(downSideVertex)
# # #
# # #                             # dodawanie informacji o punkcie dyfrakcji do obiektu
# # #                             # 'topDiffractionData'
# # #                             downSideDiffractionData.addPoint(downSideVertex, pathDifference, 2)
# # #
# # #
# # #                     #===============================================================
# # #                     # Abar  - obliczanie ekranowania na krawędzi górnej
# # #                     #===============================================================
# # #                     AbarUpSide = calcAbar(lineRS, upSideDiffractionData, data.settings, lambda500Hz, d, C2, Agr, "VERTICAL")
# # #                     AbarDownSide = calcAbar(lineRS, downSideDiffractionData, data.settings, lambda500Hz, d, C2, Agr, "VERTICAL")
                
                      
            #-------------------------------------------------------------------
            # Obliczanie całkowitego tłumienia
            #-------------------------------------------------------------------
            A = Adiv + Aatm + Agr + Abar
            
            #-------------------------------------------------------------------
            # Obliczanie poziomu dźwięku w punkcie (DW - z wiatrem)
            #-------------------------------------------------------------------
            LDW = pointSource.LWA + pointSource.DC - A
            
            if data.settings["ALTERNATIVE_AGR_CALC"]:
                # w alternatywnej metodzie trzeba uwzględnić inne DO
                LDW = LDW - pointSource.DO + DOAlternative
            
            LDWList.append(LDW)
            
            # uwzględnianie dyfrakcji na krawędziach bocznych
            if data.settings["SIDE_DIFFRACTION_CALC"]:
                
                if AbarUpSide != 0:
                    AUpSide = Adiv + Aatm + Agr + AbarUpSide
                    LDWUpSide = pointSource.LWA + pointSource.DC - AUpSide
                    
                    if data.settings["ALTERNATIVE_AGR_CALC"]:
                        # w alternatywnej metodzie trzeba uwzględnić inne DO
                        LDWUpSide = LDWUpSide - pointSource.DO + DOAlternative
                    
                    LDWList.append(LDWUpSide)
                    
                if AbarDownSide != 0:
                    ADownSide = Adiv + Aatm + Agr + AbarDownSide
                    LDWDownSide = pointSource.LWA + pointSource.DC - ADownSide
                    
                    if data.settings["ALTERNATIVE_AGR_CALC"]:
                        # w alternatywnej metodzie trzeba uwzględnić inne DO
                        LDWDownSide = LDWDownSide - pointSource.DO + DOAlternative
                    
                    LDWList.append(LDWDownSide)
        
        # gdy przeliczone zostaną wszystkie źródła wykonujemy sumowanie energetyczne
        LDWArray = numpy.array(LDWList)
        ELDWArray = 10 ** (0.1 * LDWArray)
        ELDWSum = sum(ELDWArray)
        LDWSum = 10 * numpy.log10(ELDWSum)
        
        resultArray[iCalcPoint] = calcPoint.X, calcPoint.Y, calcPoint.Z, LDWSum
        
        resultFile.write('{0}\t{1}\t{2}\n'.format(calcPoint.X, calcPoint.Y, LDWSum))
        
#         print '{0}\t{1}\t{2}\n'.format(calcPoint.X, calcPoint.Y, LDWSum)
        
    resultFile.close()
    
    resultSHP = os.path.join(data.settings["RESULTS_FOLDER"], "results.shp")
    
    # nadpisujemy poprzedni wynik
    if arcpy.Exists(resultSHP):
        arcpy.Delete_management(resultSHP)
        
    # konwersja tablicy do SHP
    arcpy.da.NumPyArrayToFeatureClass(resultArray, resultSHP, ['X', 'Y', 'Z'])

    
    # wyplot - testy
    
#     x = resultArray['X']
#     y = resultArray['Y']
#     ldw = resultArray['LDW']
#     
#     points  = numpy.hstack((x,y))
#     
#     xMin = min(x)
#     xMax = max(x)
#     yMin = min(y)
#     yMax = max(y)
#     
#     XI, YI = numpy.mgrid[round(xMin):round(xMax), round(yMin):round(yMax)]
#     from scipy.interpolate import griddata
# #     grid_z0 = griddata(points, resultArray['LDW'], (grid_x, grid_y), method='nearest')
# #     grid_z1 = griddata(points, resultArray['LDW'], (grid_x, grid_y), method='linear')
# #     grid_z2 = griddata(points, resultArray['LDW'], (grid_x, grid_y), method='cubic')
#     
#     from scipy.interpolate import Rbf
#     import matplotlib.pyplot as plt
#     from matplotlib import cm
#     rbf = Rbf(x, y, ldw, epsilon=2)
#     ZI = rbf(XI, YI)
#     plt.pcolor(XI, YI, ZI, cmap=cm.jet)
#     plt.scatter(x, y, 100, ldw, cmap=cm.jet)
#     
#     plt.show()
#     
# #     import matplotlib.pyplot as plt
# #     plt.subplot(221)
# #     plt.subplot(222)
# #     plt.imshow(grid_z0.T, origin='lower')
# #     plt.title('Nearest')
# #     plt.subplot(223)
# #     plt.imshow(grid_z1.T, origin='lower')
# #     plt.title('Linear')
# #     plt.subplot(224)
# #     plt.imshow(grid_z2.T, origin='lower')
# #     plt.title('Cubic')
# #     plt.gcf().set_size_inches(6, 6)
# #     plt.show()