FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://system.conf file://appliance-ca.cert.pem"
RAUC_KEYRING_FILE = "appliance-ca.cert.pem"
