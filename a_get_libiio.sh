# For Ubuntu 20.04 or Debian 11 (Bullseye)
wget -nc -q "https://github.com/analogdevicesinc/libiio/releases/download/v0.24/libiio-0.24.gc4498c2-Linux-Ubuntu-20.04.deb"

# Extract libiio
dpkg -x libiio-0.24.gc4498c2-Linux-Ubuntu-20.04.deb libiio

# Get path of the extracted libiio
LIBIIO_PATH=$(pwd)/libiio/usr/lib/x86_64-linux-gnu/

# Print message to user
# echo "libiio library files are in $LIBIIO_PATH"

echo "To use libiio, add the following path to your LD_LIBRARY_PATH environment variable:"
echo "$LIBIIO_PATH"
echo "To make this setting permanent, please edit your ~/.bashrc file."

echo ""
echo ""
echo "Now, please activate your python virtual environment with pyadi-iio"

