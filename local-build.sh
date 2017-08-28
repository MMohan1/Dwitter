# Uncomment the following lines if you want the script to set up your virtualenv for you:
virtualenv dwitter_venv
source dwitter_venv/bin/activate

# Install dependencies and setup data
pip install -r requirements.txt
python manage.py makemigration
python manage.py migrate
python manage.py runserver
