SUMMARY = "Field-updated appliance image"
LICENSE = "MIT"
inherit core-image
IMAGE_INSTALL:append = " rauc appliance-health"
IMAGE_FSTYPES = "ext4 wic"
