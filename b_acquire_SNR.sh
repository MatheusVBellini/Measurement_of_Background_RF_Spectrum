
echo "Please, execute this script inside a (virtual) environment with pyadi"

# Get the path of libiio library files (guess)
LIBIIO_PATH=$(pwd)/libiio/usr/lib/x86_64-linux-gnu/
export LD_LIBRARY_PATH="$LIBIIO_PATH:$LD_LIBRARY_PATH"

python3 acquire_SNR.py
