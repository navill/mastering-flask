#!/bin/sh
#!/bin/bash
if [ ! -d "venv" ]; then
    echo --------------------
    echo Creating virtualenv
    echo --------------------
    python3 -m venv venv
fi
source venv/bin/activate

pip install -r requirements.txt

export FLASK_APP=main.py
if [ ! -d "migrations" ]; then
    echo --------------------
    echo INIT THE migrations folder
    echo --------------------
    # export FLASK_APP=main.py; flask db init
    export FLASK_APP=main.py; python manage.py db init
fi
echo --------------------
echo Generate migration DDL code
echo --------------------
python manage.py db init
echo --------------------
echo Run the DDL code and migrate
echo --------------------
echo --------------------
echo This is the DDL code that will be run
echo --------------------
python manage.py db upgrade
echo --------------------
echo Generating test data
echo --------------------
source venv/bin/activate; python test_data.py

