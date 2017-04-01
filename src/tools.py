# -*- coding: utf-8 -*-
__author__ = "Michał Kowalczuk"
__copyright__ = "Copyright 2013, Michał Kowalczuk"

import arcpy
import os
import shutil
import calc
# import multiprocessing as mp

# import model

#===============================================================================
# CREATE PROJECT
#===============================================================================
class CreateProjectTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1. Create Project"
        self.description = ""
        self.canRunInBackground = False
        
        self.calcType = "Receiver"
 
    def getParameterInfo(self):
        """Define parameter definitions"""
          
        # folder projektu    
        paramProjectFolder = arcpy.Parameter(displayName="Project Folder",
                                             name="projectFolder",
                                             datatype="DEFolder",
                                             parameterType="Required",
                                             direction="Input")
        
        # tworzenie szablonu plików wejściowych
        paramGenerateTemplate = arcpy.Parameter(displayName="Generete Template",
                                                name="generateTemplate",
                                                datatype="GPBoolean",
                                                parameterType="Optional",
                                                direction="Input")
        paramGenerateTemplate.value = True
 
        params = [paramProjectFolder, paramGenerateTemplate]
         
        return params
 
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
 
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return
 
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
 
    def execute(self, parameters, messages):
        """The source code of the tool."""
         
        projectFolder = parameters[0].valueAsText
        generateTemplate = parameters[1]
        
        dataFolder = os.path.join(projectFolder, 'DATA')
        resultsFolder = os.path.join(projectFolder, 'RESULTS')
        tempFolder = os.path.join(projectFolder, 'TEMP')

        if os.listdir(projectFolder):
            shutil.rmtree(projectFolder)
            os.mkdir(projectFolder)
            
        # tworzenie niezbędnych folderów
        os.mkdir(dataFolder)
        os.mkdir(resultsFolder)
        os.mkdir(tempFolder)
        
        # i geobazy
        arcpy.CreateFileGDB_management(dataFolder, "data.gdb")
        
        # tworzenie szablonów plików wejściowych
        if generateTemplate.value:
            
            # ścieżki plików wejściowych
            pointSourcesPath = os.path.join(dataFolder, 'PointSources.shp')
            lineSourcesPath = os.path.join(dataFolder, 'LineSources.shp')
            areaSourcesPath = os.path.join(dataFolder, 'AreaSources.shp')
#             verticalAreaSourcesPath = os.path.join(dataFolder, 'VerticalAreaSources.shp')
            buildingsPath = os.path.join(dataFolder, 'Buildings.shp')
            noiseWallsPath = os.path.join(dataFolder, 'NoiseWalls.shp')
            groundAreasPath = os.path.join(dataFolder, 'GroundAreas.shp')
            receiversPath = os.path.join(dataFolder, 'Receivers.shp')
            calcAreasPath = os.path.join(dataFolder, 'CalcAreas.shp')
            
            # źródła punktowe
            arcpy.CreateFeatureclass_management(dataFolder, # out_path
                                                'PointSources', # out_name
                                                'POINT', # geometry_type
                                                '#', # template
                                                'ENABLED', # has_m
                                                'ENABLED', # has_z
                                                None) # spatial_reference
            arcpy.AddField_management(pointSourcesPath, 'NAME', 'TEXT')
            arcpy.AddField_management(pointSourcesPath, 'HEIGHT', 'DOUBLE')
            arcpy.AddField_management(pointSourcesPath, 'LWA', 'DOUBLE')
            arcpy.AddField_management(pointSourcesPath, 'DI', 'DOUBLE')
            arcpy.AddField_management(pointSourcesPath, 'REF_PLANES', 'SHORT')
            
            # źródła liniowe
            arcpy.CreateFeatureclass_management(dataFolder, # out_path
                                                'LineSources', # out_name
                                                'POLYLINE', # geometry_type
                                                '#', # template
                                                'ENABLED', # has_m
                                                'ENABLED', # has_z
                                                None) # spatial_reference
            arcpy.AddField_management(lineSourcesPath, 'NAME', 'TEXT')
            arcpy.AddField_management(lineSourcesPath, 'HEIGHT', 'DOUBLE')
            arcpy.AddField_management(lineSourcesPath, 'LWA', 'DOUBLE')
            arcpy.AddField_management(lineSourcesPath, 'LWA_TYPE', 'SHORT')
            arcpy.AddField_management(lineSourcesPath, 'V_KM_H', 'SHORT')
            arcpy.AddField_management(lineSourcesPath, 'N', 'LONG')
            
            # źródła powierzchniowe
            arcpy.CreateFeatureclass_management(dataFolder, # out_path
                                                'AreaSources', # out_name
                                                'POLYGON', # geometry_type
                                                '#', # template
                                                'ENABLED', # has_m
                                                'ENABLED', # has_z
                                                None) # spatial_reference
            arcpy.AddField_management(areaSourcesPath, 'NAME', 'TEXT')
            arcpy.AddField_management(areaSourcesPath, 'HEIGHT', 'DOUBLE')
            arcpy.AddField_management(areaSourcesPath, 'LWA', 'DOUBLE')
            arcpy.AddField_management(areaSourcesPath, 'LWA_TYPE', 'SHORT')
            
            # budynki
            arcpy.CreateFeatureclass_management(dataFolder, # out_path
                                                'Buildings', # out_name
                                                'POLYGON', # geometry_type
                                                '#', # template
                                                'ENABLED', # has_m
                                                'ENABLED', # has_z
                                                None) # spatial_reference
            arcpy.AddField_management(buildingsPath, 'NAME', 'TEXT')
            arcpy.AddField_management(buildingsPath, 'H', 'DOUBLE')
            
            # ekrany
            arcpy.CreateFeatureclass_management(dataFolder, # out_path
                                                'NoiseWalls', # out_name
                                                'POLYLINE', # geometry_type
                                                '#', # template
                                                'ENABLED', # has_m
                                                'ENABLED', # has_z
                                                None) # spatial_reference
            arcpy.AddField_management(noiseWallsPath, 'NAME', 'TEXT')
            arcpy.AddField_management(noiseWallsPath, 'H', 'DOUBLE')
            arcpy.AddField_management(noiseWallsPath, 'DL_ALFA', 'SHORT')
            
            # grunt
            arcpy.CreateFeatureclass_management(dataFolder, # out_path
                                                'GroundAreas', # out_name
                                                'POLYGON', # geometry_type
                                                '#', # template
                                                'ENABLED', # has_m
                                                'ENABLED', # has_z
                                                None) # spatial_reference
            arcpy.AddField_management(groundAreasPath, 'NAME', 'TEXT')
            arcpy.AddField_management(groundAreasPath, 'G', 'DOUBLE')
            
            # receptory
            arcpy.CreateFeatureclass_management(dataFolder, # out_path
                                                'Receivers', # out_name
                                                'POINT', # geometry_type
                                                '#', # template
                                                'ENABLED', # has_m
                                                'ENABLED', # has_z
                                                None) # spatial_reference
            arcpy.AddField_management(receiversPath, 'NAME', 'TEXT')
            arcpy.AddField_management(receiversPath, 'HEIGHT', 'DOUBLE')
            
            # obszary obliczeń
            arcpy.CreateFeatureclass_management(dataFolder, # out_path
                                                'CalcAreas', # out_name
                                                'POLYGON', # geometry_type
                                                '#', # template
                                                'ENABLED', # has_m
                                                'ENABLED', # has_z
                                                None) # spatial_reference
            arcpy.AddField_management(calcAreasPath, 'NAME', 'TEXT')
            arcpy.AddField_management(calcAreasPath, 'HEIGHT', 'DOUBLE')
            
        return

#===============================================================================
# IMPORT DATA
#===============================================================================
class ImportDataTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2. Import Data"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # folder projektu    
        paramProjectFolder = arcpy.Parameter(displayName="Project Folder",
                                             name="projectFolder",
                                             datatype="DEFolder",
                                             parameterType="Required",
                                             direction="Input")
          
        # źródła punktowe
        paramPointSourcesPath = arcpy.Parameter(displayName="Point Sources",
                                                name="pointSourcesPath",
                                                datatype="DEFeatureClass",
                                                parameterType="Optional",
                                                direction="Input")
          
        # źródła liniowe
        paramLineSourcesPath = arcpy.Parameter(displayName="Line Sources",
                                               name="lineSourcesPath",
                                               datatype="DEFeatureClass",
                                               parameterType="Optional",
                                               direction="Input")
          
        # źródła powierzchniowe
        paramAreaSourcesPath = arcpy.Parameter(displayName="Area Source",
                                               name="areaSourcesPath",
                                               datatype="DEFeatureClass",
                                               parameterType="Optional",
                                               direction="Input")
          
        # budynki
        paramBuildingsPath = arcpy.Parameter(displayName="Buildings",
                                             name="buildingsPath",
                                             datatype="DEFeatureClass",
                                             parameterType="Optional",
                                             direction="Input")
          
        # ekrany
        paramNoiseWallsPath = arcpy.Parameter(displayName="Noise Walls",
                                              name="noiseWallsPath",
                                              datatype="DEFeatureClass",
                                              parameterType="Optional",
                                              direction="Input")
          
        # grunt
        paramGroundAreasPath = arcpy.Parameter(displayName="Ground Areas",
                                               name="groundAreasPath",
                                               datatype="DEFeatureClass",
                                               parameterType="Optional",
                                               direction="Input")
          
        # receptory
        paramReceiversPath = arcpy.Parameter(displayName="Receivers",
                                            name="receiversPath",
                                            datatype="DEFeatureClass",
                                            parameterType="Optional",
                                            direction="Input")
          
        # obszary obliczeń
        paramCalcAreasPath = arcpy.Parameter(displayName="Calc Areas",
                                             name="calcAreasPath",
                                             datatype="DEFeatureClass",
                                             parameterType="Optional",
                                             direction="Input")
          
        # dokładność XY
        paramXYTolerance = arcpy.Parameter(displayName="XY Tolerance [m]",
                                           name="XYTolerance",
                                           datatype="GPDouble",
                                           parameterType="Required",
                                           direction="Input")
        paramXYTolerance.value = 0.001
          
        # tylko aktualizacja
        paramOnlyUpdate = arcpy.Parameter(displayName="Only Update",
                                          name="onlyUpdate",
                                          datatype="GPBoolean",
                                          parameterType="Required",
                                          direction="Input")
        paramOnlyUpdate.value = False
   
        params = [paramProjectFolder, # 0
                  paramPointSourcesPath, # 1
                  paramLineSourcesPath, # 2
                  paramAreaSourcesPath, # 3
                  paramBuildingsPath, # 4
                  paramNoiseWallsPath, # 5
                  paramGroundAreasPath, # 6
                  paramReceiversPath, # 7
                  paramCalcAreasPath, # 8
                  paramXYTolerance, # 9
                  paramOnlyUpdate] # 10
           
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        onlyUpdate = parameters[10].value
          
        # po podaniu katalogu projektu wypełniane zostaną ścieżki do plików
        if parameters[0].value and not onlyUpdate and not (parameters[1].altered or
                                                           parameters[2].altered or
                                                           parameters[3].altered or
                                                           parameters[4].altered or
                                                           parameters[5].altered or
                                                           parameters[6].altered or
                                                           parameters[7].altered or
                                                           parameters[8].altered):
               
            dataFolder = os.path.join(parameters[0].valueAsText, 'DATA')
               
            parameters[1].value = os.path.join(dataFolder, 'PointSources.shp')
            parameters[2].value = os.path.join(dataFolder, 'LineSources.shp')
            parameters[3].value = os.path.join(dataFolder, 'AreaSources.shp')
               
            parameters[4].value = os.path.join(dataFolder, 'Buildings.shp')
            parameters[5].value = os.path.join(dataFolder, 'NoiseWalls.shp')
            parameters[6].value = os.path.join(dataFolder, 'GroundAreas.shp')
               
            parameters[7].value = os.path.join(dataFolder, 'Receivers.shp')
            parameters[8].value = os.path.join(dataFolder, 'CalcAreas.shp')
         
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        projectFolder = parameters[0].valueAsText
          
        pointSourcesPath = parameters[1].valueAsText
        lineSourcesPath = parameters[2].valueAsText
        areaSourcesPath = parameters[3].valueAsText
          
        buildingsPath = parameters[4].valueAsText
        noiseWallsPath = parameters[5].valueAsText
        groundAreasPath = parameters[6].valueAsText
          
        receiversPath = parameters[7].valueAsText
        calcAreasPath = parameters[8].valueAsText
          
        XYTolerance = parameters[9].valueAsText
        arcpy.env.XYTolerance = XYTolerance + ' Meters'
          
# # #         onlyUpdate = parameters[10].value
          
        dataGDBPath = os.path.join(projectFolder,'DATA','data.gdb')
        
        if pointSourcesPath:
            arcpy.CopyFeatures_management(pointSourcesPath, dataGDBPath + '\\PointSources')
        if lineSourcesPath:
            arcpy.CopyFeatures_management(lineSourcesPath, dataGDBPath + '\\LineSources')
        if areaSourcesPath:
            arcpy.CopyFeatures_management(areaSourcesPath, dataGDBPath + '\\AreaSources')
        if buildingsPath:
            arcpy.CopyFeatures_management(buildingsPath, dataGDBPath + '\\Buildings')
        if noiseWallsPath:
            arcpy.CopyFeatures_management(noiseWallsPath, dataGDBPath + '\\NoiseWalls')
        if groundAreasPath:
            arcpy.CopyFeatures_management(groundAreasPath, dataGDBPath + '\\GroundAreas')
        if receiversPath:
            arcpy.CopyFeatures_management(receiversPath, dataGDBPath + '\\Receivers')
        if calcAreasPath:
            arcpy.CopyFeatures_management(calcAreasPath, dataGDBPath + '\\CalcAreas')
        
        
            
        
# # #         if onlyUpdate:
# # # #             updatePath = ''
# # #             if pointSourcesPath:
# # #                 arcpy.Delete_management(dataGDBPath + '\\PointSources')
# # # #                 updatePath =+ pointSourcesPath + ';'
# # #             if lineSourcesPath:
# # #                 arcpy.Delete_management(dataGDBPath + '\\LineSources')
# # # #                 updatePath =+ lineSourcesPath + ';'
# # #             if areaSourcesPath:
# # #                 arcpy.Delete_management(dataGDBPath + '\\AreaSources')
# # # #                 updatePath =+ areaSourcesPath + ';'
# # #             if buildingsPath:
# # #                 arcpy.Delete_management(dataGDBPath + '\\Buildings')
# # # #                 updatePath =+ buildingsPath + ';'
# # #             if noiseWallsPath:
# # #                 arcpy.Delete_management(dataGDBPath + '\\NoiseWalls')
# # # #                 updatePath =+ noiseWallsPath + ';'
# # #             if groundAreasPath:
# # #                 arcpy.Delete_management(dataGDBPath + '\\GroundAreas')
# # # #                 updatePath =+ groundAreasPath + ';'
# # #             if receiversPath:
# # #                 arcpy.Delete_management(dataGDBPath + '\\Receivers')
# # # #                 updatePath =+ receiversPath + ';'
# # #             if calcAreasPath:
# # #                 arcpy.Delete_management(dataGDBPath + '\\CalcAreas')
# # # #                 updatePath =+ calcAreasPath + ';'
# # #                   
# # #           
# # #         arcpy.FeatureClassToGeodatabase_conversion(pointSourcesPath + ';' +
# # #                                                    lineSourcesPath + ';' +
# # #                                                    areaSourcesPath + ';' +
# # #                                                    buildingsPath + ';' +
# # #                                                    noiseWallsPath + ';' +
# # #                                                    groundAreasPath + ';' +
# # #                                                    receiversPath + ';' +
# # #                                                    calcAreasPath,
# # #                                                    dataGDBPath)
        return

#===============================================================================
# RUN PROJECT
#===============================================================================
class RunProjectTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "3. Run Project"
        self.description = ""
        self.canRunInBackground = False
 
    def getParameterInfo(self):
        """Define parameter definitions"""
         
        # folder projektu    
        paramProjectFolder = arcpy.Parameter(displayName="Project Folder",
                                             name="projectFolder",
                                             datatype="DEFolder",
                                             parameterType="Required",
                                             direction="Input")
        
        # nazwa obliczeń  
        paramCalcName = arcpy.Parameter(displayName="Calculation name",
                                       name="calcName",
                                       datatype="GPString",
                                       parameterType="Required",
                                       direction="Input")
        
        # katalog wyników  
        paramResultsFolder = arcpy.Parameter(displayName="Results Folder",
                                            name="resultsFolder",
                                            datatype="GPString",
                                            parameterType="Required",
                                            direction="Input",
                                            enabled = False)        
        
        # CALC_TYPE
        paramCalcType = arcpy.Parameter(displayName="Calculation type",
                                        name="calcType",
                                        datatype="GPString",
                                        parameterType="Required",
                                        direction="Input")
        paramCalcType.filter.type = "ValueList"
        paramCalcType.filter.list = ["Receiver", "Grid"]
        paramCalcType.value = "Receiver"
        
        # DETAILED_RESULTS
        paramDetailedResults = arcpy.Parameter(displayName="Enable detailed results",
                                               name="detailedResults",
                                               datatype="GPBoolean",
                                               parameterType="Required",
                                               direction="Input")
        paramDetailedResults.value = True


        # CALCULATION SETTINGS -------------------------------------------------
        
        # TIME_PERIOD   
        paramTimePeriod = arcpy.Parameter(displayName="Time period [h]",
                                          name="timePeriod",
                                          datatype="GPDouble",
                                          parameterType="Required",
                                          direction="Input",
                                          category="Calculation Settings")
        paramTimePeriod.value = 1
        
        # SPACING_CALC 
        paramSpacingCalc = arcpy.Parameter(displayName="Grid space [m]",
                                           name="spacingCalc",
                                           datatype="GPDouble",
                                           parameterType="Required",
                                           direction="Input",
                                           category="Calculation Settings")
        paramSpacingCalc.value = 10
        
        # MAX_RADIUS_CALC
        paramMaxRadiusCalc = arcpy.Parameter(displayName="Max search radius [m]",
                                            name="maxRadiusCalc",
                                            datatype="GPLong",
                                            parameterType="Required",
                                            direction="Input",
                                            category="Calculation Settings")
        paramMaxRadiusCalc.value = 1000
        
        # MAX_ABAR_SINGLE_CALC
        paramMaxABarSingleCalc = arcpy.Parameter(displayName="Limitation of single diffraction [dB]",
                                                 name="maxABarSingleCalc",
                                                 datatype="GPLong",
                                                 parameterType="Required",
                                                 direction="Input",
                                                 category="Calculation Settings")
        paramMaxABarSingleCalc.value = 20
        
        # MAX_ABAR_DOUBLE_CALC
        paramMaxABarDoubleCalc = arcpy.Parameter(displayName="Limitation of multiple diffraction [dB]",
                                                 name="maxABarDoubleCalc",
                                                 datatype="GPLong",
                                                 parameterType="Required",
                                                 direction="Input",
                                                 category="Calculation Settings")
        paramMaxABarDoubleCalc.value = 25
        
        # SIDE_DIFFRACTION_CALC
        paramSideDiffractionCalc = arcpy.Parameter(displayName="Enable side diffraction",
                                                  name="sideDiffractionCalc",
                                                  datatype="GPBoolean",
                                                  parameterType="Required",
                                                  direction="Input",
                                                  category="Calculation Settings")
        paramSideDiffractionCalc.value = True
        
        # ALTERNATIVE_AGR_CALC
        # alternatywna metoda obliczania wpływu gruntu
        paramAlternativeAgrCalc = arcpy.Parameter(displayName="Enable alternative method of ground attenuation calculation (Agr)",
                                                  name="alternativeAgrCalc",
                                                  datatype="GPBoolean",
                                                  parameterType="Required",
                                                  direction="Input",
                                                  category="Calculation Settings")
        paramAlternativeAgrCalc.value = False
        
        # ALTERNATIVE_ABAR_CALC
        # uwzględnij tylko dodatnie wartości Agr w obliczaniu Abar
        paramAlternativeAbarCalc = arcpy.Parameter(displayName="Use only positive values of ground attenuation (Agr) in screening calculation (Abar)",
                                                   name="alternativeAbarCalc",
                                                   datatype="GPBoolean",
                                                   parameterType="Required",
                                                   direction="Input",
                                                   category="Calculation Settings")
        paramAlternativeAbarCalc.value = True
                
                
        # MODEL SETTINGS -------------------------------------------------------
        
        # MIN_STEP_LINESOURCE
        paramMinStepLinesource = arcpy.Parameter(displayName="Minimal step for dividing line sources [m]",
                                                 name="minStepLinesource",
                                                 datatype="GPDouble",
                                                 parameterType="Required",
                                                 direction="Input",
                                                 category="Model Settings")
        paramMinStepLinesource.value = 1
        
        # DHMAX_RATIO_LINESOURCE
        # stosunek odległości do maksymalnego wymiaru źródła liniowego
        # paragraf 4.c normy: d>2Hmax (opcja minimalna)
        paramDHMaxRatioLinesource = arcpy.Parameter(displayName="Distance to largest dimension of source ratio (d>2Hmax) [m]",
                                                    name="dHMaxRatioLinesource",
                                                    datatype="GPDouble",
                                                    parameterType="Required",
                                                    direction="Input",
                                                    category="Model Settings")
        paramDHMaxRatioLinesource.value = 8
        
        # STEP_AREASOURCE
        paramStepAreasource = arcpy.Parameter(displayName="Step for dividing area source [m]",
                                                    name="stepAreasource",
                                                    datatype="GPDouble",
                                                    parameterType="Required",
                                                    direction="Input",
                                                    category="Model Settings")
        paramStepAreasource.value = 10
        
        # G_GROUNDAREA
        paramGGroundArea = arcpy.Parameter(displayName="Default ground area (0 - hard, 1 - soft)",
                                                    name="gGroundArea",
                                                    datatype="GPDouble",
                                                    parameterType="Required",
                                                    direction="Input",
                                                    category="Model Settings")
        paramGGroundArea.value = 1 # grunt porowaty
        
        
        #ENVIRONMENT -----------------------------------------------------------
        
        # TEMPERATURE
        paramTemperature = arcpy.Parameter(displayName="Temperature [" + u'\u2103' + "]",
                                           name="temperature",
                                           datatype="GPDouble",
                                           parameterType="Required",
                                           direction="Input",
                                           category="Environment")
        paramTemperature.value = 10
        
        # HUMIDITY
        paramHumidity = arcpy.Parameter(displayName="Humidity [%]",
                                        name="humidity",
                                        datatype="GPLong",
                                        parameterType="Required",
                                        direction="Input",
                                        category="Environment")
        paramHumidity.value = 70
        
        # ATMOSPHERIC_PRESSURE
        paramAtmosphericPpressure = arcpy.Parameter(displayName="Atmospheric Ppressure [hPa]",
                                                    name="atmosphericPressure",
                                                    datatype="GPDouble",
                                                    parameterType="Required",
                                                    direction="Input",
                                                    category="Environment")
        paramAtmosphericPpressure.value = 1013.25 # (101.325 kPa)
        
        
        # PARAMS ---------------------------------------------------------------        
        params = [paramProjectFolder, # 0
                  paramCalcName, # 1
                  paramResultsFolder, #2
                  paramCalcType, # 3
                  paramDetailedResults, # 4
                  paramTimePeriod, # 5
                  paramSpacingCalc, # 6
                  paramMaxRadiusCalc, # 7
                  paramMaxABarSingleCalc, # 8
                  paramMaxABarDoubleCalc, # 9
                  paramSideDiffractionCalc, # 10
                  paramAlternativeAgrCalc, # 11
                  paramAlternativeAbarCalc, # 12
                  paramMinStepLinesource, # 13
                  paramDHMaxRatioLinesource, # 14
                  paramStepAreasource, # 15
                  paramGGroundArea, # 16
                  paramTemperature, # 17
                  paramHumidity, # 18
                  paramAtmosphericPpressure] # 19
        
        return params
 
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
 
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        projectFolder = parameters[0].valueAsText
        calcName = parameters[1].valueAsText
        
        if projectFolder and calcName:
            parameters[2].value = os.path.join(projectFolder, "RESULTS", calcName)
              
        return
 
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
 
    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        # DEBUGGING ------------------------------------------------------------
        """
        projectFolder = r"C:\_DANE\GIS\Studia\Praca Dyplomowa\Grunwaldzka\IsoNoise"
        dataGDBPath = os.path.join(projectFolder,'DATA','data.gdb')
        resultsFolder = r"C:\_DANE\GIS\Studia\Praca Dyplomowa\Grunwaldzka\IsoNoise\RESULTS\grid_debug"
        
        # słownik ustawień
        settings = {}
        settings["GEODATABASE"] = dataGDBPath
        settings["RESULTS_FOLDER"] = resultsFolder
        settings["SPATIAL_REFERENCE"] = None
        
        settings["CALC_TYPE"] = "Grid"
        settings["DETAILED_RESULTS"] = False
        settings["TIME_PERIOD"] = 1
        
        # ustawienia obliczeń
        settings["SPACING_CALC"] = 25
        settings["MAX_RADIUS_CALC"] = 1000
        settings["MAX_ABAR_SINGLE_CALC"] = 20
        settings["MAX_ABAR_DOUBLE_CALC"] = 25
        settings["SIDE_DIFFRACTION_CALC"] = False
        
        # alternatywna metoda obliczania wpływu gruntu
        settings["ALTERNATIVE_AGR_CALC"] = True
        # uwzględnij tylko dodatnie wartości Agr w obliczaniu Abar
        settings["ALTERNATIVE_ABAR_CALC"] = True
        
        # parametry obiektów modelu
        settings["MIN_STEP_LINESOURCE"] = 5
        # stosunek odległości do maksymalnego wymiaru źródła liniowego
        # paragraf 4.c normy: d>2Hmax (opcja minimalna)
        settings["DHMAX_RATIO_LINESOURCE"] = 2
        settings["STEP_AREASOURCE"] = 10
        settings["G_GROUNDAREA"] = 1
        
        # meteo
        settings["TEMPERATURE"] = 10
        settings["HUMIDITY"] = 70
        settings["ATMOSPHERIC_PRESSURE"] = 1013.25
        
        if os.path.exists(resultsFolder):
            shutil.rmtree(resultsFolder)
            
        os.mkdir(resultsFolder)
        
        # END OF DEBUGGING -----------------------------------------------------
        """
        projectFolder = parameters[0].valueAsText
        dataGDBPath = os.path.join(projectFolder,'DATA','data.gdb')
        
        resultsFolder = parameters[2].valueAsText
        
        if os.path.exists(resultsFolder):
            shutil.rmtree(resultsFolder)
            
        os.mkdir(resultsFolder)
        
        # słownik ustawień
        settings = {}
        settings["GEODATABASE"] = dataGDBPath
        settings["RESULTS_FOLDER"] = resultsFolder
        settings["SPATIAL_REFERENCE"] = None
        
        settings["CALC_TYPE"] = parameters[3].valueAsText
        settings["DETAILED_RESULTS"] = parameters[4].value
        settings["TIME_PERIOD"] = parameters[5].value
        
        # ustawienia obliczeń
        settings["SPACING_CALC"] = parameters[6].value
        settings["MAX_RADIUS_CALC"] = parameters[7].value
        settings["MAX_ABAR_SINGLE_CALC"] = parameters[8].value
        settings["MAX_ABAR_DOUBLE_CALC"] = parameters[9].value
        settings["SIDE_DIFFRACTION_CALC"] = parameters[10].value
        
        # alternatywna metoda obliczania wpływu gruntu
        settings["ALTERNATIVE_AGR_CALC"] = parameters[11].value
        # uwzględnij tylko dodatnie wartości Agr w obliczaniu Abar
        settings["ALTERNATIVE_ABAR_CALC"] = parameters[12].value
        
        # parametry obiektów modelu
        settings["MIN_STEP_LINESOURCE"] = parameters[13].value
        # stosunek odległości do maksymalnego wymiaru źródła liniowego
        # paragraf 4.c normy: d>2Hmax (opcja minimalna)
        settings["DHMAX_RATIO_LINESOURCE"] = parameters[14].value
        settings["STEP_AREASOURCE"] = parameters[15].value
        settings["G_GROUNDAREA"] = parameters[16].value
        
        # meteo
        settings["TEMPERATURE"] = parameters[17].value
        settings["HUMIDITY"] = parameters[18].value
        settings["ATMOSPHERIC_PRESSURE"] = parameters[19].value
        
        # ----------------------------------------------------------------------
        
        # utworzenie klasy z danymi wejściowymi
        data = calc.Data(settings)
         
        # dodawanie danych do modelu
        data.addPointSources(dataGDBPath + "\\PointSources")
        data.addLineSources(dataGDBPath + "\\LineSources")
        data.addAreaSources(dataGDBPath + "\\AreaSources")
        data.addBuildings(dataGDBPath + "\\Buildings")
        data.addNoiseWalls(dataGDBPath + "\\NoiseWalls")
        data.addGroundAreas(dataGDBPath + "\\GroundAreas")
         
        if settings["CALC_TYPE"] == "Receiver":
            data.addReceivers(dataGDBPath + "\\Receivers")
        elif settings["CALC_TYPE"] == "Grid":
            data.addCalcAreas(dataGDBPath + "\\CalcAreas")
        else:
            print "Wrong CALC_TYPE"
        
#         arcpy.SetProgressorLabel("Trwają obliczenia")
# # #         pool = mp.Pool(2)
# # #         pool.map(calc.run,(data,data))
# # #         pool.close()
# # #         pool.join()
        
        # uruchomienie obliczeń
        calc.run(data)
        
        arcpy.ResetProgressor()
        
        return
