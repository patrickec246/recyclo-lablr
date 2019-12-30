yum install perl-devel

cd static
gzip -dc exiftool.tar.gz | tar -xf -
cd Image-ExifTool-11.78
perl Makefile.PL
sudo make install

if [ ! -f /usr/bin/exiftool ]; then
	if [ -f /usr/local/bin/exiftool ]; then
		echo "Moving exiftool"
		mv /usr/local/bin/exiftool /usr/bin/exiftool
	fi
fi

cd ../..
pip3 install -r requirements.txt
