# IsoNoiose
This is programming part of my diploma thesis at GIS postgraduate studies at University of Gdańsk called:

*Noise propagation model. Implementation of International Standard ISO 9613-2 “Acoustics – Attenuation of sound during propagation outdoors – Part 2: General method of calculation”*

It is an ArcGIS Python Toolbox (Python + ArcPy and Numpy packages). To use it you need ArcGIS Desktop software >= 10.0. 

To find more check [poster](https://github.com/michkowalczuk/IsoNoise/blob/master/poster/Michal_Kowalczuk_Noise_propagation_model.png?raw=true).

In IsoNoise Python Toolbox there are 3 tools:

![isonoise-toolbox](https://user-images.githubusercontent.com/23641410/29656670-6ac62e74-88b5-11e7-9b4e-865445434595.PNG)


1. Create Project - define project folder. Toolbox will optionally generate a template for model features (buildings, point sources, calculation areas, etc.)

![1-create-project](https://user-images.githubusercontent.com/23641410/29656666-6a9c70b6-88b5-11e7-8b84-eb2888cff91e.PNG)


2. Import Data - give a paths to project features. Optionally you can only update some of them.

![2-import-data](https://user-images.githubusercontent.com/23641410/29656669-6ac4c0fc-88b5-11e7-8ef1-dbb1b10456d8.PNG)


3. Run Project - start calculations. You can choose calculation type: Receiver or Grid. Furthermore, you have a lot of settings, so if you know *ISO 9613-2 Standard* you can get into depth. If not just leave defaults.

![3-run-project](https://user-images.githubusercontent.com/23641410/29656671-6ac6700a-88b5-11e7-85ad-d02eefb2db89.PNG)


* Calculation Settings

![calculation-settings](https://user-images.githubusercontent.com/23641410/29656673-6ac6c1d6-88b5-11e7-8d6f-572baeed7ba6.PNG)


* Environment Settings

![environment](https://user-images.githubusercontent.com/23641410/29656672-6ac6b83a-88b5-11e7-925f-06dc1481fa82.PNG)


* Model Settings

![model-settings](https://user-images.githubusercontent.com/23641410/29656668-6ab7d694-88b5-11e7-93c1-e6b4641b3cac.PNG)


Using other interpolation tools you can prepare maps with noise level areas like below:

![results-map](https://user-images.githubusercontent.com/23641410/29657974-9facd5f8-88b9-11e7-8b91-74be8a7b0e88.PNG)
