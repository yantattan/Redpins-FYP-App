======= Packages installation ========
Using an IDE
Navigate to /app/src/main/assets/webapp
Under terminal, run "pip install -r requirements.txt"

OR
Using command prompt
cd <path to main project folder>/app/src/main/assets/webapp
pip install -r requirements.txt


======== Running the application ========
To run the app on website, from the root project folder navigate to /app/src/main/assets/webapp

In the directory, run python file __init__.py. * Python 3 is required in order to run the webapp.

Raw html pages are location at /app/src/main/assets/webapp/templates/pages


======== Running on emulator ========
*Running on emulator is discouraged as navbar might not fit for smaller phones and GPS location services are not working due to latest version blocking usage of location services from Javascript solution.
*Android Studio is required for installation.
*Running emulator should only be used when testing scanning of QR codes

To run the application on emulator, run the web application first.
From the folders directory menu, navigate to java/<first folder>, right click on MainActivity.kt and select run. This might up to 2-5 minutes on the first run.


======== Install an emulator ========
To Install an emulator, go to AVD manager located at the top of Android Studio. 
Select Pixel 5 API 30, and click on "Show Advanced Settings"
Scroll down, and under Camera, change front and back to Webcam, then click Finish.


