. ~/env/bin/activate
git clone https://github.com/KryptoPX/django-musician

cd django-musician
pip install -r requirements.txt

cp .env.example .env
sed -i 's/https:\/\/api.examplea.org/http:\/\/127.0.0.1:9999\/api/g' .env
echo "STATIC_ROOT=/tmp/" >> .env

cd django-musician 
python manage.py runserver 8080