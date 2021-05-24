# Flask App


## **Description**

A Flask App which Performs Kmean Clustering on a Hospital Dataset,to find optimal locations for placement of Oxygen Plants.Google Maps Api is used to render to a JavascriptMap, Geocode and Reverse Geocode.

## **Algorithm used**
Kmean-Clustering

 ## **Implementation**
Whenever an user enters a particular latitude and Longitude, Map is rendered with the entered coordinates as center and the result of clstering is displaed. 
**Note:** currently the implementation is done only for the state of Karnataka(due to lack of oxygen plants data), the model can be deployed for any dataset.

## **Installation** 

- Create a virtual environment in root project directory - python3 -m venv env

- Activate the env - source env/bin/activate(Linux),env/Scripts/activate(Windows)

- Install dependencies - pip install -r requirements.txt

- Run export/set FLASK_APP=new.py in terminal

- Run export/set FLASK_env=development

- Run flaskrun

