#  SEEDS
**SEEDS stands for Stakeholder-Based Environmentally-sustainable And Economically Doable Scenarios for the Energy Transition**

In the SEEDS project a consortium of four European institutions is building an approach to integrate humans into energy transition scenario design, while accurately modelling the relevant technical, economic and environmental constraints. Doing so involves methodological development, software development and implementation, and experimentation with a pilot study in Portugal.
This work is done in a focused consortium of four partners:

1. `ETHZ` is a leading centre of high-resolution energy system modelling
2. `ICTA-UAB` is a leading centre in the development of integrated sustainability assessment methods
3. `TLU` provides expertise in participatory design of trustworthy interactive systems
4. `FC.ID` contributes its unique expertise combining modelling with participatory action research.

# Setting up and Running SEEDS app

The following steps offers guidlines on setting up & running SEEDS app on local machine.

### Clone the SEEDS repository

```
git clone https://github.com/centre-for-educational-technology/Seeds_bootstrap
```

### Install the required packages

```
cd Seeds_bootstrap
pip install -r ./requirement.txt
```

### Initialise SEEDS database

```
python3 manage.py makemigrations
python3 manage.py migrate --run-syncdb
```

### Populate the database
The seeds dataset comprises multiple CSV files which were processed to store in the database. To populate the database with SEEDS data, we will use a script `loadAll.py` available in the `scripts` directory. The following command performs the loading of data into the SEEDS database.

```
python3 manage.py shell < ./scripts/loadAll.py
```

### Create a superuser account
The following command creates an admin user account for the app.

```
python3 manage.py createsuperuser
```

### Run the server
Everything is set now to run the server.

```
python3 manage.py runserver
```

# License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


```python

```
