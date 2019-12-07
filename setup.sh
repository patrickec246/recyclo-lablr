cd static
gzip -dc exiftool.tar.gz | tar -xf -
cd Image-ExifTool-11.78
perl Makefile.PL
sudo make install
cd ../..
pip3 install -r requirements.txt
