import arcpy
import os
import sys

srcDir = os.path.join(os.path.dirname(__file__), "src")
sys.path.append(srcDir)

from tools import CreateProjectTool, ImportDataTool, RunProjectTool

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "IsoNoise"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CreateProjectTool, ImportDataTool, RunProjectTool]


# DEBUGGING --------------------------------------------------------------------

# def main():
#     tbx = Toolbox()
#     tool = RunProjectTool()
#     tool.execute(tool.getParameterInfo(), None)
#      
# if __name__ == "__main__":
#     main()
