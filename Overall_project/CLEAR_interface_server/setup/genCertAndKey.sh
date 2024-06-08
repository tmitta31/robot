#!/bin/bash

# Determine the directory where the script resides
# SCRIPT_DIR="$( cd ../"$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR="../security"

# Ensure the 'security' directory exists, create it if not
if [ ! -d "$REPO_PATH" ]; then
    mkdir -p $DIR
fi

# Set filenames with full path
KEY_FILE="$DIR/key.pem"
CERT_FILE="$DIR/cert.pem"

# Set default certificate field values
C="XX"              # Country
ST="CLEAR"     # State
L="CLEAR"   # Locality
O="CLEAR"       # Organization
OU="CLEAR"   # Organizational Unit
CN="CLEAR"      # Common Name
EMAIL="CLEAR@CLEAR.com"

# Generate a new private key
openssl genpkey -algorithm RSA -out $KEY_FILE

# Generate a self-signed certificate with the provided default values
openssl req -new -x509 -key $KEY_FILE -out $CERT_FILE -days 365 \
-subj "/C=$C/ST=$ST/L=$L/O=$O/OU=$OU/CN=$CN/emailAddress=$EMAIL"

echo "Successfully created $KEY_FILE and $CERT_FILE."
