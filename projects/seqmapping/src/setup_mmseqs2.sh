#!/bin/sh
# Created by Tongji Xing 09/10/2024

mmsdir=/opt/mmseqs2

# Download the AVX2 binary provided by mmseqs2 developers. More info at https://github.com/soedinglab/MMseqs2
sudo curl -L "https://github.com/soedinglab/MMseqs2/releases/download/15-6f452/mmseqs-linux-avx2.tar.gz" -o /opt/mmseqs-linux-avx2.tar.gz


sudo mkdir $mmsdir
# Unpacks it under mmseqs2
sudo tar -zxvf /opt/mmseqs-linux-avx2.tar.gz -C $mmsdir --strip-components=1

echo "# Linking /usr/local/bin/mmseqs to $mmsdir/bin/mmseqs"
sudo ln -s $mmsdir/bin/mmseqs /usr/local/bin/mmseqs
