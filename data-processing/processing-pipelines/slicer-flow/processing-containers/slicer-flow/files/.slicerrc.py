import os
documentsLocation = qt.QStandardPaths.DocumentsLocation
documents = qt.QStandardPaths.writableLocation(documentsLocation)
databaseDirectory = os.path.join(documents, slicer.app.applicationName + "DICOMDatabase")
dicomBrowser = ctk.ctkDICOMBrowser()
dicomBrowser.databaseDirectory = databaseDirectory
dicomBrowser.createNewDatabaseDirectory()
