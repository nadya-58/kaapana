import os
documentsLocation = qt.QStandardPaths.DocumentsLocation
documents = qt.QStandardPaths.writableLocation(documentsLocation)
databaseDirectory = os.path.join(documents, slicer.app.applicationName + "DICOMDatabase")
dicomBrowser = ctk.ctkDICOMBrowser()
dicomBrowser.databaseDirectory = databaseDirectory
dicomBrowser.createNewDatabaseDirectory()

# generate config file for mpReview

# input

# output  
kaapanaOutputDir = os.path.join(os.getenv('WORKFLOW_DIR'))
cmd1 = '/bin/mkdir -p %s' % kaapanaOutputDir
os.system(cmd1)

kaapanaOutputFileName = os.path.join(kaapanaOutputDir, 'batch',ref_seriesUID,'slicer-results','result.dcm')
cmd2 = '/bin/cp %s %s' % ( labelFileName, kaapanaOutputFileName )
os.system(cmd2)


config = os.path.join("mpReview/Resources/mpReview_remote_kaapana_configuration_hierarchy2.json")
f = open(config)
f.write("username": "deepa", 
	"database_type": "remote",
	"remote_database_configuration": 
		{
			"project_id":"",
			"location_id":"",
			"dataset_id":"",
			"dicomstore_id":"", 
			"other_server_url":"http://dcm4chee-service.services.svc:8080/dcm4chee-arc/aets/KAAPANA/rs"
		},

    "uids":[
        {
            "StudyInstanceUID":"1.3.6.1.4.1.14519.5.2.1.3671.4754.121472087445374646718121301133",
            "SeriesInstanceUID_list": ["1.3.6.1.4.1.14519.5.2.1.3671.4754.983460207615355998147518323000"]
        },
        {
            "StudyInstanceUID":"1.3.6.1.4.1.14519.5.2.1.3671.4754.288848219213026850354055725664",
            "SeriesInstanceUID_list": ["1.3.6.1.4.1.14519.5.2.1.3671.4754.609837242670719860929372097937"]
        }
	],
	
	"output_configuration":
		{
                "output_directory: %s" % kaapanaOutputDir, 
                "output_mapping:   %s" % kaapanaOutputFileName
		},
		
	"terminology": "SegmentationCategoryTypeModifier-mpReview.json"


        )
f.close
