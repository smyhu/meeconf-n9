#!/bin/sh
# make-deb.sh - builds meeconf-n9_<VER>_all.deb from app/ + art/ + packaging/
set -e
D=$(cd "$(dirname "$0")/.." && pwd)
VER=$(sed -n "s/^APP_VERSION = '\(.*\)'/\1/p" $D/app/main.py)
OUTDIR=${OUTDIR:-$D/dist}
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
P=$T/data
mkdir -p $P/opt/meeconf-n9/qml $P/usr/share/applications $P/usr/share/icons/hicolor/80x80/apps $P/usr/share/doc/meeconf-n9 $T/ctl
install -m 755 $D/app/main.py $P/opt/meeconf-n9/
install -m 644 $D/app/core.py $P/opt/meeconf-n9/
install -m 644 $D/app/qml/*.qml $D/app/qml/*.js $D/app/qml/*.png $P/opt/meeconf-n9/qml/
install -m 644 $D/packaging/meeconf-n9.desktop $P/usr/share/applications/
install -m 644 $D/art/meeconf-n9.png $P/usr/share/icons/hicolor/80x80/apps/
install -m 644 $D/LICENSE $P/usr/share/doc/meeconf-n9/copyright
SIZE=$(du -sk $P | cut -f1)
cat > $T/ctl/control <<CTL
Package: meeconf-n9
Version: $VER
Architecture: all
Maintainer: smyhu <smyhu@users.noreply.github.com>
Installed-Size: $SIZE
Depends: python (>= 2.6), python-pyside.qtdeclarative, python-pyside.qtgui, python-dbus, qt-components
Section: user/utilities
Priority: optional
Homepage: https://github.com/smyhu/meeconf-n9
Description: Bulk setup of e-mail accounts
 Creates accounts for the Nokia N9 Mail app by hand or from a CSV file
 (Excel / OnlyOffice), fills in the servers of known providers and can
 export the existing accounts to CSV. Passwords are entered in Mail on the
 first refresh, as for accounts made by hand. Languages: en, pl.
 Designed and written by Claude (Anthropic) together with smyhu.
Maemo-Display-Name: MeeConf
Maemo-Flags: visible
CTL
printf 'Maemo-Icon-26: %s\n' "$(base64 -w0 $D/art/meeconf-n9.png)" >> $T/ctl/control
(cd $P && find . -type f | sed 's#^\./##' | sort | xargs md5sum) > $T/ctl/md5sums
(cd $T/ctl && tar czf ../control.tar.gz --owner=0 --group=0 --numeric-owner --format=gnu ./control ./md5sums)
(cd $P && tar czf ../data.tar.gz --owner=0 --group=0 --numeric-owner --format=gnu .)
echo 2.0 > $T/debian-binary
mkdir -p $OUTDIR; DEB=$OUTDIR/meeconf-n9_${VER}_all.deb; rm -f $DEB
(cd $T && ar rc $DEB debian-binary control.tar.gz data.tar.gz)
md5sum $DEB
