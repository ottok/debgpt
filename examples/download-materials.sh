mkdir -p pytorch/debian
wget -c 'https://salsa.debian.org/deeplearning-team/pytorch/-/raw/master/debian/rules?ref_type=heads&inline=false' -O pytorch/debian/rules
wget -c 'https://salsa.debian.org/deeplearning-team/pytorch/-/raw/master/debian/control?ref_type=heads' -O pytorch/debian/control
mkdir -p fish/debian
wget -c 'https://salsa.debian.org/debian/fish/-/raw/master/debian/control?ref_type=heads' -O fish/debian/control
wget -c 'https://salsa.debian.org/debian/fish/-/raw/master/debian/rules?ref_type=heads&inline=false' -O fish/debian/rules

curl 'https://salsa.debian.org/deeplearning-team/pytorch/-/raw/master/debian/patches/nvfuser.patch?ref_type=heads' -o nvfuser.patch
