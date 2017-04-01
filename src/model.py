#-*- coding: utf-8 -*-
__author__ = "Michał Kowalczuk"
__copyright__ = "Copyright 2013, Michał Kowalczuk"

import arcpy
import math

#===============================================================================
# GŁÓWNA KLASA BAZOWA ELEMENTÓW MODELU
#===============================================================================
class BaseModelElement(object):
    """Klasa bazowa dla wszystkich obiektów modelu"""

    # konstruktor
    def __init__(self, height=0.0, name="ModelElement"):
        
        self._height = height
        self._name = name
    
    @property
    def Height(self):
        """Zwraca wysokość nad poziomem gruntu obiektu"""
        return self._height
    
    @property
    def Name(self):
        """Zwraca nazwę obiektu"""
        return self._name

#===============================================================================
# KLASA BAZOWA PUNKTÓW
#===============================================================================
class BasePoint(BaseModelElement):
    """Klasa bazowa dla punktów"""

    # konstruktor
    def __init__(self, point=arcpy.Geometry(), height=0.0, name="Point"):
                
        # do określenia współrzędnej Z obiektu wymagana jego wysokość 
        # nad powierzchnią gruntu (height)
        BaseModelElement.__init__(self, height, name)
        
        self.point = point
        
        # z pliku ZAWSZE importujemy elewację punktu,
        # czyli wysokość nad poziomem morza jego rzutu na powierzchnię gruntu
        self._elevation = self.point.getPart(0).Z
        
        # geometria typu 'arcpy.PointGeometry' MUSI przechowywać rzeczywistą
        # wysokość obiektu, dlatego współrzędną 'Z' zwiększamy o 'Height'
        if height != 0:
            # ustalamy rzeczywistą wysokość źródła
            self.point = arcpy.PointGeometry(arcpy.Point(self.X, self.Y, self.Z), None, True)
            
    def __str__(self):
        """Metoda do obsługi print"""
        return "X: {0}, Y: {1}, Z: {2}, ELEVATION: {3}, HEIGHT: {4}".format(self.X,
                                                                            self.Y,
                                                                            self.Z,
                                                                            self.Elevation,
                                                                            self.Height)

#    def SetXYZ(self, X, Y, Z):
#        """Tworzy obiekt arcpy.PointGeometry dla instancji klasy BasePoint"""
#        self.point=arcpy.PointGeometry(arcpy.Point(X, Y, Z), None, True)

    @property
    def X(self):
        """Zwraca współrzędną X punktu"""
        return self.point.getPart(0).X

    @property
    def Y(self):
        """Zwraca współrzędną Y punktu"""
        return self.point.getPart(0).Y
    
    @property
    def Elevation(self):
        """Zwraca elewację obiektu"""
        return self._elevation
    
    @property
    def Z(self):
        """Zwraca współrzędną Z obiektu"""
        return self.Elevation + self.Height
    
    @property
    def Point(self):
        """Zwraca punkt w postaci obiektu 'arcpy.Point'"""
        return self.point.getPart(0)
    
    @property
    def PointGeometry(self):
        """Zwraca punkt w postaci obiektu 'arcpy.PointGeometry'"""
        return self.point
    
    def distanceTo(self, otherPoint):
        "Zwraca odległość do wkazanego punktu"
        return self.point.distanceTo(otherPoint.point)

#===============================================================================
# KLASA BAZOWA POLILINI
#===============================================================================
class BasePolyline(BaseModelElement):
    """Klasa bazowa dla polilini"""

    # konstruktor
    def __init__(self, polyline=arcpy.Geometry(), height=0.0, name="Polyline"):
        
        self._polyline = polyline
        BaseModelElement.__init__(self, height, name)
        
###        # sprawdzanie czy polilinia ma zmienną wysokość
###        if polyline.Length3D - polyline.Length > 0.0:
###            self._floatingHeight = True
###        else:
###            self._floatingHeight = False
            
###        if not self._floatingHeight:
            
###        # ustalamy rzeczywistą wysokość źródła
###        # lista wierzchołków polilinii
###        polylineVerticesArray = polyline.getPart(0)
###        adjustedVerticesArray = arcpy.Array()
###        # pętla po każdym wierzhołku
###        
###        for vertex in polylineVerticesArray:
###            
###            # tworzymy nowy punkt ze zmienioną Height i dodajemy do listy
###            adjustedPoint = arcpy.Point(vertex.X, vertex.Y, height)
####                adjustedPoint = arcpy.Point(vertex.X, vertex.Y, vertex.Z + elevation) - tymczasowo rezygnuję z tej metody
###            adjustedVerticesArray.append(adjustedPoint)
###
###        # tworzymy nową polilinię
###        self.polyline = arcpy.Polyline(adjustedVerticesArray, None, True)
###    else:
###        self.polyline = polyline

    @property
    def Polyline(self):
        """Zwraca obiekt 'arcpy.Polyline'"""
        return self._polyline
    
    @property
    def Length(self):
        """Zwraca długość rzutu polilini na płaszczyznę XY"""
        return self._polyline.length

    @property
    def Length3D(self):
        """Zwraca rzeczywistą długość źródła liniowego"""
        return self._polyline.length3D
    
# # #     @property
# # #     def VerticesArray(self):
# # #         verticesArray = self._polyline.getPart(0)
# # #         return verticesArray
# # #     
# # #     @property
# # #     def VerticesList(self):
# # #         verticesList = []
# # #         for vertex in self.VerticesArray:
# # #             verticesList.append(vertex)
# # #             
# # #         return verticesList

#===============================================================================
# KLASA BAZOWA POLIGONÓW
#===============================================================================
class BasePolygon(BaseModelElement):
    """Klasa bazowa dla poligonów"""

    # konstruktor
    def __init__(self, polygon=arcpy.Geometry(), height=0.0, name="Area"):

        BaseModelElement.__init__(self, height, name)
        self._polygon = polygon

###        #  geometria typu arcpy.Polygon
###        if height != 0:
###            # ustalamy rzeczywistą wysokość poligonu
###            # lista wierzchołków poligonu
###            polygonVerticesArray = polygon.getPart(0)
###            adjustedVerticesArray = arcpy.Array()
###            # pętla po każdym wierzhołku
###            for vertex in polygonVerticesArray:
###                # tworzymy nowy punkt z zmienioną wsp. Z i dodajemy do listy
###                adjustedPoint = arcpy.Point(vertex.X, vertex.Y, vertex.Z + elevation)
###                adjustedVerticesArray.append(adjustedPoint)
###
###            # tworzymy nowy poligon
###            self.Polygon = arcpy.Polygon(adjustedVerticesArray, None, True)
###        else:
###            self.Polygon = polygon

    # WŁASNOŚCI -------------------------------------------------------------------
    @property
    def Polygon(self):
        """Zwraca obiekt 'arcpy.Polygon'"""
        return self._polygon
    
    @property
    def Area(self):
        """Zwraca powierzchnię poligonu"""
        return self._polygon.area
    
    @property
    def Elevation(self):
        """Zwraca elewację obiektu - średnia z wszystkich wierzchołków"""
        
        vertices = self._polygon.getPart(0)
        noVertices = self._polygon.pointCount - 1
        zMean = 0
        
        # obliczanie średniej współrzędnej Z
        for iVertex in range(noVertices):
            zMean += vertices[iVertex].Z
            
        # obliczanie elewacji
        elevation = zMean / noVertices
                
        return elevation
    
# # #     @property
# # #     def VerticesArray(self):
# # #         verticesArray = self._polygon.getPart(0)
# # #         verticesCount = verticesArray.count
# # #         verticesArray.remove(verticesCount - 1)
# # #         
# # #         return verticesArray
# # #     
# # #     @property
# # #     def VerticesList(self):
# # #         verticesList = []
# # #         for vertex in self.VerticesArray:
# # #             verticesList.append(vertex)
# # #             
# # #         return verticesList
    
            
#===============================================================================
# KLASA POINT_SOURCE
#===============================================================================
class PointSource(BasePoint):
    """Źródło punktowe"""

    # konstruktor
    def __init__(self, point=arcpy.Geometry(), height=0.0, lwa=0.0, di=0,
                 reflectingPlanes=0, name="PointSource"):

        BasePoint.__init__(self, point, height, name)

        # poziom mocy w dBA
        self._lwa = lwa

        # Directivity Index - współczynnik kierunkowości
        self._di = di

        # Directivity Omega - promieniowanie w kącie bryłowym
        if reflectingPlanes == 0 and height != 0.0:
            self._reflectingPlanes = 1
        else:
            self._reflectingPlanes = reflectingPlanes
        
    def __str__(self):
        """Metoda do obsługi print"""
        return "{0}\t{1}\t{2}\t{3}\t{4}".format(self.X,
                                                self.Y,
                                                self.Z,
                                                self.Height,
                                                self.LWA)

    @property
    def LWA(self):
        """Zwraca poziom mocy"""
        return self._lwa

    # Directivity Index
    @property
    def DI(self):
        """Zwraca współczynnik kierunkowości"""
        return self._di

    @property
    def Q(self):
        """Zwraca część kąta bryłowego, do którego promieniuje źródło"""
        return 2 ** self._reflectingPlanes

    # Directivity Omega
    @property
    def DO(self):
        """Zwraca współczynnik związany z liczbą powierzchni odbijających"""
        return 10 * math.log10(self.Q)

    # Directivity Correction
    @property
    def DC(self):
        """Zwraca poprawkę kierunkowości DC - wzór (3) normy"""
        return self.DI + self.DO
    
#===============================================================================
# KLASA LINE_SOURCE
#===============================================================================
class LineSource(BasePolyline):
    """Źródło liniowe"""

    # konstruktor
    def __init__(self, polyline=arcpy.Geometry(), height=0.0, lwa=0.0, lwaType=0,
                 v=0.0, n=0, name="LineSource"):

        BasePolyline.__init__(self, polyline, height, name)
        self._lwa = lwa
        self._lwaType = lwaType
        self._v = v
        self._n = n

    @property
    def LWAType(self):
        """Zwraca rodzaj poziomu mocy"""
        return self._lwaType
    
    def getLWA(self, segmentLength=0.0):
        """Oblicza poziom mocy źródła liniowego"""
        # określanie poziomu mocy na dBA/m
        if self._lwaType == 0:
            # poziom mocy źródła źródła liniowego wyrażona w dBA/m (DEFAULT)
            lwa = self._lwa + 10 * math.log10(segmentLength)
            
        elif self._lwaType == 1:
            # całkowity poziom mocy źródła liniowego w dBA
            lwa = self._lwa + 10 * math.log10(segmentLength / self.Length3D)
            
        elif self._lwaType == 2:
            # poziom mocy N źródeł punktowych poruszających się z prędkością V
            if self._n != 0:
# # #                 lwa = self._lwa - 10 * math.log10(self._v) - 30 + 10 * math.log10(self._n) + 10 * math.log10(segmentLength)
                lwa = self._lwa + 10 * math.log10(self._n * segmentLength / self._v) - 30
            else:
                lwa = 0
            
        else:
            # błędny parametr 'LWA_TYPE'
            self._lwa = 0.0
        
        return lwa

###    def toPointSources(self, maxStep):
###        """Tworzy źródła punktowe z źródła liniowego.
###        maxStep - maksymalna odległość pomiędzy kolejnymi źródłami punktowymi.
###        Polilinia jest dzielona na linie - segmenty,
###        dla każdego segmentu sprawdzana jest liczba sub-segmentów
###        niedłuższych niż maxStep.
###        Dla każdego segmentu ZAWSZE powstaje min 1 sub-segment."""
###
###        # tworzenie pustych list na obiekty PointSource
###        pointSourceList = []
###        pointGeometryList = []
###
###        # odczytanie współrzędnych źródła liniowego (polyline)
###        polylinePartsArray = self.polyline.getPart(0)
###        polylinePointsCount = self.polyline.pointCount
###
###        # oętla po segmentach polilinii
###        for iPoint in range(polylinePointsCount - 1):
###
###            # tworzenie segmentu
###            segmentVerticesArray = arcpy.Array()
###            segmentVerticesArray.append(polylinePartsArray[iPoint])
###            segmentVerticesArray.append(polylinePartsArray[iPoint + 1])
###
###            # tworzenie polilinii z aktualnego segmentu
###            segmentPolyline = arcpy.Polyline(segmentVerticesArray, None, True) # dorobić settings["SPATIAL_REFERENCE"]
###
###            # długość segmentu
###            segmentLength = segmentPolyline.length
###            segmentLength3D = segmentPolyline.length3D
###
###            # metoda 'positionAlongLine' liczy długość tylko w 2D,
###            # dlatego trzeba obliczyć dodatkowy współczynnik
###            # 'tales' bo z prawa Talesa
###            talesFactor = segmentLength / segmentLength3D
###
###            # obliczanie właściwości sub-segmentów
###            subSegmentCount = int(ceil(segmentLength3D / maxStep))
###            subSegmentLength3D = segmentLength3D / subSegmentCount
###
###            # parametr do w/w metody 'positionAlongLine'
###            subSegmentAlongLineLength = subSegmentLength3D * talesFactor
###
###            # pętla po wszystkich sub-segmentach
###            for iSubSegment in range(subSegmentCount):
###                
###                # odczytujemy współrzędne środka sub-segmentu
###                position = subSegmentAlongLineLength * ( 0.5 + iSubSegment)
###                pointAlongLine = segmentPolyline.positionAlongLine(position)
###
###                # tworzenie źródła punktowego na podstawie punktu (PointGeometry)
###                tmpPointSource = PointSource(pointAlongLine,
###                                             pointAlongLine.getPart(0).Z, # ELEVATION
###                                             self.Height,
###                                             self.LWA,
###                                             name=self.Name)
###
###                # uaktualnianie listy
###                pointSourceList.append(tmpPointSource)
###                pointGeometryList.append(pointAlongLine)
###
###        arcpy.CopyFeatures_management(pointGeometryList,
###                                      r"C:\_DANE\PROGRAMOWANIE\python\Projects\ISO9613_2\data\tmp.gdb\pointsAlongLine_" + str(iPoint) + "_" + str(iSubSegment))
###
###        # zwracamy listę źródeł punktwych
###        return pointSourceList

#===============================================================================
# KLASA AREA_SOURCE
#===============================================================================
class AreaSource(BasePolygon):
    """Źródło powierzchniowe"""

    # konstruktor
    def __init__(self, polygon=arcpy.Geometry(), height=0.0, lwa=0.0, lwaType=0,
                 name="AreaSource"):
        
        BasePolygon.__init__(self, polygon, height, name)

        # określanie poziomu mocy na dBA/m2
        if lwaType == 0:
            # poziom mocy źródła źródła powierzchniowego w dBA/m2 (DEFAULT)
            self._lwa = lwa
            
        elif lwaType == 1:
            # całkowity poziom mocy źródła powierzchniowego w dBA
            self._lwa = lwa - 10 * math.log10(self.Area)
            
        else:
            # błędny wybór LWA_TYPE
            self._lwa = 0.0

    @property
    def LWA(self):
        """Zwraca poziom mocy w dBA/m2"""
        return self._lwa

    def toPointSources(self, step):
        """Tworzy źródła punktowe z źródła powierzchniowego.
        step - rozmiar siatki
        Emisja z powierzchni każdego kafelka modelowana jest źródłem punktowym"""
        
        #-----------------------------------------------------------------------
        # Metoda 1 - szybsza, ale używa troszkę więcej pamięci
        # W zakresie poligonu tworzona jest siatka (FISHNET),
        # siatka przecinana z poligonem źródła powierzchniowego
        # w centroidze każdego powstałego kafelka umieszczane jest źródło punktowe
        # o poziomie mocy proporcjanalnym do pola powierzchni elementu
        #-----------------------------------------------------------------------

        # zakres poligonu (extent)
        xMin = self.Polygon.extent.XMin
#        xMax=self.Polygon.extent.XMax
        width = self.Polygon.extent.width

        yMin = self.Polygon.extent.YMin
        yMax = self.Polygon.extent.YMax
        height = self.Polygon.extent.height

        # lewy dolny róf siatki (origin of the fishnet)
        originCoordinate = '{0} {1}'.format(xMin, yMin)

        # kierunek osi Y (orientation)
        yAxisCoordinate = '{0} {1}'.format(xMin, yMax)

        # bok siatki
        cellSizeWidth = str(step)
        cellSizeHeight = str(step)

        # liczba wierszy i kolumn siatki
        numRows = str(int(math.ceil(height / step)))
        numColumns = str(int(math.ceil(width / step)))
        
        # żeby FISHNET I INTERSECT działał prawidłowo wyłączam chwilowo 'outputZFlag'
        arcpy.env.outputZFlag = "Disabled"
        
        # fishnet tworzony w pamięci 'in_memory',
        # bo nie można bezpośrednio gi użyć klasy w 'Intersect'
        arcpy.CreateFishnet_management(r'in_memory\fishnet',
                                       originCoordinate, yAxisCoordinate,
                                       cellSizeWidth, cellSizeHeight,
                                       numRows, numColumns,
                                       '#', "NO_LABELS", '#', "POLYGON")

        # poligon źródła powierzchniowego kopiowany do pamięci,
        # w celu wykonania 'Intersect'
        arcpy.CopyFeatures_management(self.Polygon, r'in_memory\areaSource')
      
        # przecięcie siatki ze źródłem powierzchniowym
        areaSourceTiles = arcpy.Intersect_analysis([r'in_memory\fishnet', r'in_memory\areaSource'], #r"C:\_DANE\PROGRAMOWANIE\python\Projects\ISO9613_2\data\tmp.gdb\areaSourceFishnet",
                                                   arcpy.Geometry(),
                                                   'ONLY_FID', '#', 'INPUT')
        
        arcpy.env.outputZFlag = "Enabled"
        
        # listy punktów
        pointSourceList = []
        pointGeometryList = []

        # elewacja źródła powierzchniwego (przyjmuję średnią)
        zMean = 0
        for iVertex in range(self.Polygon.pointCount - 1):
            zMean += self.Polygon.getPart(0)[iVertex].Z
            
        zMean /= (self.Polygon.pointCount - 1)
        
        # inne opcje
#        z = self.Polygon.centroid.Z
#        z = self.Polygon.getPart(0)[0].Z

        # pętla po każdym kafelku źródła powierzchniwego
        for part in areaSourceTiles:

            # poziom mocy proporcjonalny do powierzchni kafelka
            lwa = self._lwa + 10 * math.log10(part.area)
            
            # ustalanie położenia źródła zastępczego
            tmpCentroid = part.centroid
            tmpPoint = arcpy.PointGeometry(arcpy.Point(tmpCentroid.X, tmpCentroid.Y, zMean),
                                           None, True)
            tmpPointSource = PointSource(tmpPoint, self.Height, lwa, name=self.Name)

            # uaktualnianie listy
            pointSourceList.append(tmpPointSource)
            pointGeometryList.append(tmpPoint)

#         arcpy.CopyFeatures_management(pointGeometryList,
#                                       r"C:\_DANE\PROGRAMOWANIE\python\Projects\ISO9613_2\data\tmp.gdb\areaPointsFishnet")
        
        # zwracamy listę źródeł punktwych
        return pointSourceList


#===============================================================================
# KLASA VERTICAL_AREA_SOURCE - do zrobienia
#===============================================================================
class VerticalAreaSource(BasePolygon):
    """Pionowe źródło powierzchniowe - na razie nie będę wykorzystywał"""

    # konstruktor
    def __init__(self, polygon=arcpy.Geometry(), elevation=0.0, h = 0.0, lwa=0.0, lwaType=0,
                 name="AreaSource"):
        
        # konstruktor klasy bazowej tu nie zadziała
        BasePolygon.__init__(self, polygon, elevation, name)

        # określanie poziomu mocy na dBA/m2
        if lwaType == 0:
            # poziom mocy źródła źródła powierzchniowego w dBA/m2 (DEFAULT)
            self._lwa=lwa
        elif lwaType == 1:
            # całkowity poziom mocy źródła powierzchniowego w dBA
            self._lwa=lwa - 10 * math.log10(self.Area)

    @property
    def LWA(self):
        """Zwraca poziom mocy w dBA/m2"""
        return self._lwa
        
#===============================================================================
# KLASA RECEIVER
#===============================================================================
class Receiver(BasePoint):
    """Punkt imisji"""

    # konstruktor
    def __init__(self, point=arcpy.Geometry(), height=0.0, name="Receiver"):

        BasePoint.__init__(self, point, height, name)


#===============================================================================
# KLASA CALC_AREA
#===============================================================================
class CalcArea(BasePolygon):
    """Obszar obliczeń"""

    # konstruktor
    def __init__(self, polygon=arcpy.Geometry(), height=0.0, name="CalcArea"):

        BasePolygon.__init__(self, polygon, height, name)

    def makeGrid(self, spacing):

        #-----------------------------------------------------------------------
        # W zakresie poligonu tworzone są punkty zgodnie z krokiem 'spacing'
        # Jeżeli punkt leży wewnątrz poligonu - dodawny jest do listy
        #-----------------------------------------------------------------------

        # zakres poligonu (extent)
        xMin=self.Polygon.extent.XMin
        xWidth=self.Polygon.extent.width

        yMin=self.Polygon.extent.YMin
        yHeight=self.Polygon.extent.height

        # zaczynamy w punkcie oddalonym o step/2 od lewego dolnego narożnika prostokątu zakresu
        xMin += spacing / 2.0
        yMin += spacing / 2.0
        xNo = int(math.ceil(xWidth / spacing))
        yNo = int(math.ceil(yHeight / spacing))

        # lista na obiekty
        receiverList = []
        pointGeometryList = []

        # tworzymy punkty tak długo dopóki nie wyjdą poza zakres i są w środku poligonu
        for iX in range(xNo):
            x = xMin + iX * spacing

            for iY in range(yNo):
                y = yMin + iY * spacing
                
                # elewacja punktu Z=0, określana później na podstawie DTM
                tmpPoint = arcpy.PointGeometry(arcpy.Point(x, y, 0), None, True)
                
                # sprawdzamy czy punk obliczeniowy jest wewnątrz obszaru obliczeń
                if tmpPoint.within(self.Polygon):

                    # tworzenie punktu imisji na podstawie punktu (PointGeometry)
                    tmpReceiver = Receiver(tmpPoint, self.Height, self.Name)

                    # uaktualnianie listy
                    receiverList.append(tmpReceiver)
                    pointGeometryList.append(tmpPoint)

#         arcpy.CopyFeatures_management(pointGeometryList,
#                                       r"C:\_DANE\PROGRAMOWANIE\python\Projects\ISO9613_2\data\tmp.gdb\calcPoints")

        return receiverList

#===============================================================================
# KLASA BUILDING
#===============================================================================
class Building(BasePolygon):
    """Budynek"""

    # konstruktor
    def __init__(self, polygon=arcpy.Geometry(), h=0.0, name="Building"):

        BasePolygon.__init__(self, polygon, 0, name)
        self._h = h

    @property
    def H(self):
        """Zwraca wysokość budynku"""
        return self._h
    
    @property
    def VerticesArray(self):
        verticesArray = self._polygon.getPart(0)
        verticesCount = verticesArray.count
        verticesArray.remove(verticesCount - 1)
        
        for vertex in verticesArray:
            vertex.Z += self._h
            
        return verticesArray
    
    @property
    def VerticesList(self):
        verticesList = []
        for vertex in self.VerticesArray:
            verticesList.append(vertex)
            
        return verticesList

#===============================================================================
# KLASA NOISE-WALL
#===============================================================================
class NoiseWall(BasePolyline):
    """Ekran"""

    # konstruktor
    def __init__(self, polyline=arcpy.Geometry(), h=0.0, dlalfa=8, name="NoiseWall"):

        BasePolyline.__init__(self, polyline, 0, name)
        self._h = h
        self._dlalfa = dlalfa

    @property
    def H(self):
        """Zwraca wysokość ekranu"""
        return self._h
    
    @property
    def DLalfa(self):
        """Zwraca jednoliczbowy współczynnink oceny pochłaniania dźwięku ekranu"""
        return self._dlalfa
    
    @property
    def VerticesArray(self):
        verticesArray = self._polyline.getPart(0)
        
        for vertex in verticesArray:
            vertex.Z += self._h
            
        return verticesArray
    
    @property
    def VerticesList(self):
        verticesList = []
        for vertex in self.VerticesArray:
            verticesList.append(vertex)
            
        return verticesList

#===============================================================================
# KLASA GROUND-AREA
#===============================================================================
class GroundArea(BasePolygon):
    """Grunt: G=0 - grunt twardy, G=1 - grunt porowaty"""

    # konstruktor
    def __init__(self, polygon=arcpy.Geometry(), g=1.0, name="GroundArea"):

        BasePolygon.__init__(self, polygon, 0, name)
        self._g = g

    @property
    def G(self):
        """Zwraca wspołczynnik odbicia"""
        return self._g

#===============================================================================
# KLASA FOLIAGE-AREA
#===============================================================================
class FoliageArea(BasePolygon):
    """Zieleń"""

    # konstruktor
    def __init__(self, polygon=arcpy.Geometry(), h=0.0, name="FoliageArea"):

        BasePolygon.__init__(self, polygon, 0, name)

#===============================================================================
# KLASA LINE
#===============================================================================
class Line(object):
    """Klasa reprezentująca linię/odcinek (3D)"""

    # konstruktor
    def __init__(self, startPoint, endPoint, changeZ=0, dimension=3):
        tmpStartPoint = arcpy.Point()
        tmpStartPoint.clone(startPoint)
        tmpEndPoint = arcpy.Point()
        tmpEndPoint.clone(endPoint)
        
        # arcpy.Point()
        if dimension == 3:
            if changeZ == 0:
                self._startPoint = tmpStartPoint
                self._endPoint = tmpEndPoint
        #        pointsArray = arcpy.Array([startPoint, endPoint])
        #        self.line = arcpy.Polyline(pointsArray)
            else:
                tmpStartPoint.Z += changeZ
                tmpEndPoint.Z += changeZ
                self._startPoint = tmpStartPoint
                self._endPoint = tmpEndPoint
                
        elif dimension == 2:
            tmpStartPoint.Z = 0
            tmpEndPoint.Z = 0
            self._startPoint = tmpStartPoint
            self._endPoint = tmpEndPoint
            
    # WŁASNOŚCI ----------------------------------------------------------------
    @property
    def X1(self):
        """Zwraca X1"""
        return self._startPoint.X
    
    @property
    def Y1(self):
        """Zwraca Y1"""
        return self._startPoint.Y
        
    @property
    def Z1(self):
        """Zwraca Z1"""
        return self._startPoint.Z
    
    @property
    def X2(self):
        """Zwraca X2"""
        return self._endPoint.X
    
    @property
    def Y2(self):
        """Zwraca Y2"""
        return self._endPoint.Y
    
    @property
    def Z2(self):
        """Zwraca Z2"""
        return self._endPoint.Z
    
    @property
    def XMean(self):
        """Zwraca X2"""
        return (self.X1 + self.X2) / 2
    
    @property
    def YMean(self):
        """Zwraca Y2"""
        return (self.Y1 + self.Y2) / 2
    
    @property
    def ZMean(self):
        """Zwraca Z2"""
        return (self.Z1 + self.Z2) / 2
    
    # równanie parametryczne prostej
    # x = x1 + p * t
    # y = y1 + q * t
    # z = z1 + r * t
    # for t = 1 x = x2, etc
    
    @property
    def P(self):
        """Zwraca parametr p"""
        return self.X2 - self.X1
    
    @property
    def Q(self):
        """Zwraca parametr p"""
        return self.Y2 - self.Y1
    
    @property
    def R(self):
        """Zwraca parametr p"""
        return self.Z2 - self.Z1
    
    # równanie kierunkowe prostej
    # y = a * x + b
    
    @property
    def A(self):
        """Zwraca parametr a"""
        if self.Q != 0:
            a = self.Q / self.P
        else:
            a = None
            
        return a
    
    @property
    def B(self):
        """Zwraca parametr b"""
        if self.Q != 0:
            b = self.Y1 - self.A * self.X1
        else:
            b = self.Y1
            
        return b
    
    @property
    def Length(self):
        """Zwraca długość rzutu linii na płaszczyznę XY"""
        return math.sqrt(self.P ** 2 + self.Q ** 2)

    @property
    def Length3D(self):
        """Zwraca rzeczywistą długość lini"""
        return math.sqrt(self.P ** 2 + self.Q ** 2 + self.R ** 2)
    
    @ property
    def StartPoint(self):
        """Zwraca punkt początkowy odcinka jako 'arcpy.Point'"""
        return self._startPoint
    
    @ property
    def EndPoint(self):
        """Zwraca punkt początkowy odcinka jako 'arcpy.Point'"""
        return self._endPoint
    
    @ property
    def StartPointGeometry(self):
        """Zwraca punkt początkowy odcinka jako 'arcpy.PointGeometry'"""
        return arcpy.PointGeometry(self._startPoint, None, True)
    
    @ property
    def EndPointGeometry(self):
        """Zwraca punkt początkowy odcinka jako 'arcpy.PointGeometry'"""
        return arcpy.PointGeometry(self._endPoint, None, True)
        
    @ property
    def CentrePoint3D(self):
        """Zwraca punkt leżący w środku odcinka"""
        
        return arcpy.Point(self.XMean, self.YMean, self.ZMean)
    
    @ property
    def Vertices(self):
        """Zwraca punkty początkowy i końcowy jako listę obiektów 'arcpy.Point'"""
        return [self._startPoint, self._endPoint]
    
    @ property
    def Polyline(self):
        """Zwraca polilinię 2D 'arcpy.Polyline'"""
        verticesArray = arcpy.Array()
        verticesArray.add(self._startPoint)
        verticesArray.add(self._endPoint)
        return arcpy.Polyline(verticesArray)
    
    # METODY -------------------------------------------------------------------
    def getZAlong(self, x, y):
        t = self.getTAlong(x, y)
        z = self.Z1 + self.R * t
        
        return z
    #---------------------------------------------------------------------------
    def getTAlong(self, x, y):
        if abs(self.P) > 0.001:
            tx = (x - self.X1) / self.P
            t = tx
        elif abs(self.Q) > 0.001:
            ty = (y - self.Y1) / self.Q
            t = ty
            
        return t
    
    #---------------------------------------------------------------------------
    def getXYAlongFromNearPoint(self, point):
        if self.Q != 0:
            aPerpendicular = -1 / self.A
            bPerpendicular = point.Y - aPerpendicular * point.X
            
            aDifference = aPerpendicular - self.A
            xAlongLine = (self.B - bPerpendicular) / aDifference
#             yAlongLine = (aPerpendicular * self.B - self.A * bPerpendicular) / aDifference
            yAlongLine = self.A * xAlongLine + self.B
        else:
            xAlongLine = point.X
            yAlongLine = self.Y1
            
        return xAlongLine, yAlongLine
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def side(self, x, y):
        """
        Określa położenie na płaszczyźnie XY względem linii:
        > 0 - punkt leży nad linią
        < 0 - punkt leży pod linią
        """
        if abs(self.Q) > 0.001:
            if abs(self.P) > 0.001:
                side = y - self.A * x - self.B
            else:
                side = x - self.X1
            
        else:
            side = y - self.Y1
            
        side = round(side/0.001)*0.001    
        return side
    
    #---------------------------------------------------------------------------
    def makeHorizontal(self):
        startPoint = arcpy.Point(self.X1, self.Y1, self.ZMean)
        endPoint = arcpy.Point(self.X2, self.Y2, self.ZMean)
        lineHorizontal = Line(startPoint, endPoint)
        
        return lineHorizontal
    
    #---------------------------------------------------------------------------
    def pointAlong(self, d, param):
        """
        Zwraca punkt (arcpy.Point) na linii oddalony o zadaną odległość (2D)
        od jej początku lub końca
        d - odległość
        param = "from_start"/"from_end"
        """
        
        if param == "from_start":
            t = d / math.sqrt(self.P ** 2 + self.Q ** 2)
            if t <= 1:                
                x = self.X1 + self.P * t
                y = self.Y1 + self.Q * t
            else:
                x = self.X2
                y = self.Y2
                        
        elif param == "from_end":
            t = (self.Length - d) / math.sqrt(self.P ** 2 + self.Q ** 2)
            if t >= 0:
                x = self.X1 + self.P * t
                y = self.Y1 + self.Q * t
            else:
                x = self.X1
                y = self.Y1
        # współrzędna Z nie istotna, więc zero
        return arcpy.Point(x, y, 0)
    
    #---------------------------------------------------------------------------
    def pointAlong3D(self, d, param):
        """
        Zwraca punkt (arcpy.Point) na linii oddalony o zadaną odległość (3D)
        od jej początku lub końca
        d - odległość
        param = "from_start"/"from_end"
        """
        
        if param == "from_start":
            t = d / math.sqrt(self.P ** 2 + self.Q ** 2 + self.R ** 2)
            if t <= 1:                
                x = self.X1 + self.P * t
                y = self.Y1 + self.Q * t
                z = self.Z1 + self.R * t
            else:
                x = self.X2
                y = self.Y2
                z = self.Z2
                
        elif param == "from_end":
            t = (self.Length3D - d) / math.sqrt(self.P ** 2 + self.Q ** 2  + self.R ** 2)
            if t >= 0:
                x = self.X1 + self.P * t
                y = self.Y1 + self.Q * t
                z = self.Z1 + self.R * t
            else:
                x = self.X1
                y = self.Y1
                z = self.Z1
            
        return arcpy.Point(x, y, z)

    #---------------------------------------------------------------------------
    def distanceToPoint3D(self, point):
        """
        Zwraca odległość punktu 'point' od prostej 'k', którą wyznacza linia 'self'.
        Odległością tą jest długość odcinka prostej prostopadłej do 'k',
        którego końcami są punkt 'point' i przecięcie z prostą 'k'.
        """
        xp = point.X
        yp = point.Y
        zp = point.Z
        
        x1 = self.X1
        y1 = self.Y1
        z1 = self.Z1
        
        p = self.P
        q = self.Q
        r = self.R
        
        a = ((xp - x1) * q - (yp - y1) * p) ** 2
        b = ((yp - y1) * r - (zp - z1) * q) ** 2
        c = ((zp - z1) * p - (xp - x1) * r) ** 2
        
        p2q2r2 = p**2 + q**2 + r**2
        
        d = math.sqrt((a + b + c) / p2q2r2)
        
        return d
    
    #---------------------------------------------------------------------------
    def minimumDistanceToPoint3D(self, point):
        """Określa minimalną odległość punktu do odcinka"""
        
        # odległości do wierzchołków
        dist1 = pointDistance3D(self._startPoint, point)
        dist2 = pointDistance3D(self._endPoint, point)
        
        # odległość do środka
        dist3 = pointDistance3D(self.CentrePoint3D, point)
        
        # wyciąganie najmniejszej
        distList = [dist1, dist2, dist3]
        distList.sort()
        dist = distList[0]
            
        return dist
    
    #---------------------------------------------------------------------------
    def divide(self, segmentLength):
        """
        Dzieli linię na segmenty o zadanej długości i zwraca listę tych obiektów
        """
        segmentList = []
        if segmentLength >= self.Length3D:
            # jeśli wprowadzona długość większa od długości obiektu
            # zwracany ten sam obiekt
            segmentList.append(self)
        else:
            segmentCount = int(math.ceil(self.Length3D / segmentLength))
            startPoint = self._startPoint
            
            # tworzenie segmentów w pętli
            for iSegment in range(segmentCount):
                endPoint = self.pointAlong3D((iSegment + 1) * segmentLength, "from_start")
                segment = Line(startPoint, endPoint)
                if segment.Length3D > 0.001:
                    segmentList.append(segment)
                
                # ostatni punkt staje się początkowym następnej linii
                startPoint = endPoint
                
        return segmentList

    #---------------------------------------------------------------------------
    def pathDifference(self, insertionPoint):
        """ Wstawia punkt wtrącenia i oblicza różnicę dróg propagacji"""
        
#        lineRI = Line(self._startPoint, insertionPoint)
#        lineIS = Line(insertionPoint, self._endPoint)
#        
#        dss = lineIS.Length3D
#        dsr = lineRI.Length3D
        
        d = self.Length3D
        dsr = pointDistance3D(self._startPoint, insertionPoint)
        dss = pointDistance3D(insertionPoint, self._endPoint)
        
        pathDifference = dss + dsr - d
        return pathDifference

    #---------------------------------------------------------------------------
    def diffrationPathSegments(self, point1, point2=None):
        """Zwraca długości trzech odcinków fali ugiętej - dsr, e, dss"""
        
        if point2 == None:
            # 1 krawędź dyfrakcji
            dsr = pointDistance3D(self._startPoint, point1)
            dss = pointDistance3D(point1, self._endPoint)
            e = 0
            
        else:
            # 2 krawędzie dyfrakcji
            distR1 = pointDistance(self._startPoint, point1)
            distR2 = pointDistance(self._startPoint, point2)
            
            # szukanie punktu leżącego bliżej odbiornika
            if distR1 < distR2:
                dsr = pointDistance3D(self._startPoint, point1)
                dss = pointDistance3D(point2, self._endPoint)
            else:
                dsr = pointDistance3D(self._startPoint, point2)
                dss = pointDistance3D(point1, self._endPoint)
                
            e = pointDistance3D(point1, point2)
        
        return dsr, e, dss


#===============================================================================
# KLASA LINE
#===============================================================================
class Edge(Line):
    """
    Klasa reprezentująca krawędź dyfrakcji - dziedziczt z klasy 'Line',
    ale dodatkowo przechowuje informacje z jakiego obiektu pochodzi.
    Element:
    1 - budynek,
    2 - ekran,
    3 - teren
    """
    
    # konstruktor
    def __init__(self, startPoint, endPoint, element, index):

        Line.__init__(self, startPoint, endPoint)
        self._element = element
        self._index = index

    @property
    def Element(self):
        """Zwraca typ elementu modelu z jakiego pochodzi krawędź"""
        return self._element
    
    @property
    def Index(self):
        """Zwraca index w danej liście elementów modelu"""
        return self._index
    
    
#===============================================================================
# FUNKCJA POINT DISTANCE 2D
#===============================================================================
def pointDistance(point1, point2):
    """Zwraca odległość (2D) między dwoma punktami"""
    
    dx = point1.X - point2.X
    dy = point1.Y - point2.Y
    
    distance = math.sqrt(dx**2 + dy**2)
    return distance
    
#===============================================================================
# FUNKCJA POINT DISTANCE 3D
#===============================================================================
def pointDistance3D(point1, point2):
    """Zwraca odległość (3D) między dwoma punktami"""
    
    dx = point1.X - point2.X
    dy = point1.Y - point2.Y
    dz = point1.Z - point2.Z
    
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    return distance