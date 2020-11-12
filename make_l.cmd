echo Make localization
cd file_to_audio
python ../manage.py makemessages -l ru
python ../manage.py makemessages -l en
python ../manage.py compilemessages
cd ..