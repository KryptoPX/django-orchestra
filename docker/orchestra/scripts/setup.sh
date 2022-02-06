. ~/env/bin/activate

git clone https://github.com/ribaguifi/django-orchestra.git
pip install -r django-orchestra/requirements.txt
pip install -e django-orchestra

orchestra-admin startproject panel

cd panel
python manage.py migrate