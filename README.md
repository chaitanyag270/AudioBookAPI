The API simulation has been done in flask, and the corresponding tests have also been written.

Prerequisites
1) Python 3.8
2) MySQl Server (Xampp)
3) create Database named "organisation"

Commands to be executed for creating Database table for the very first time only
1) enter python shell script
2) execute the following
    i)from components.models import db
   ii)db.drop_all()
   iii)db.create_all()
3) create rows in "config_file_type" table
    i)from components.models import ConfigFileType
   ii)record_1 = ConfigFileType("SONGFILE", 1)
        db.session.add(record_1)
      record_2 = ConfigFileType("AUDIOBOOKFILE", 2)
        db.session.add(record_2)
      record_3 = ConfigFileType("PODCASTBOOKFILE", 3)
        db.session.add(record_2)
