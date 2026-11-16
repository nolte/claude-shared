SUMMARY = "Health definition gating boot-complete.target"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"
SRC_URI = "file://appliance-health.service file://appliance-health"
S = "${WORKDIR}"
inherit systemd
SYSTEMD_SERVICE:${PN} = "appliance-health.service"
do_install() {
    install -Dm0644 ${S}/appliance-health.service ${D}${systemd_system_unitdir}/appliance-health.service
    install -Dm0755 ${S}/appliance-health ${D}${libexecdir}/appliance-health
}
FILES:${PN} += "${systemd_system_unitdir}/appliance-health.service"
