#!/bin/bash

set -o errexit

git status
git submodule

if [ ! "$1" ]; then
  echo "This script requires either amd64 of arm64 as an argument"
	exit 1
elif [ "$1" = "amd64" ]; then
	export REDHAT_PLATFORM="x86_64"
else
	export REDHAT_PLATFORM="arm64"
fi

# If the env variable NOTARIZE and the username and password variables are
# set, this will attempt to Notarize the signed DMG

if [ ! "$STAI_INSTALLER_VERSION" ]; then
	echo "WARNING: No environment variable STAI_INSTALLER_VERSION set. Using 0.0.0."
	STAI_INSTALLER_VERSION="0.0.0"
fi
echo "Stai Installer Version is: $STAI_INSTALLER_VERSION"

echo "Installing npm and electron packagers"
cd npm_linux || exit 1
npm ci
cd .. || exit 1

echo "Create dist/"
rm -rf dist
mkdir dist

echo "Create executables with pyinstaller"
SPEC_FILE=$(python -c 'import sys; from pathlib import Path; path = Path(sys.argv[1]); print(path.absolute().as_posix())' "pyinstaller.spec")
pyinstaller --log-level=INFO "$SPEC_FILE"
LAST_EXIT_CODE=$?
if [ "$LAST_EXIT_CODE" -ne 0 ]; then
	echo >&2 "pyinstaller failed!"
	exit $LAST_EXIT_CODE
fi

# Creates a directory of licenses
echo "Building pip and NPM license directory"
pwd
bash ./build_license_directory.sh

# Builds CLI only rpm
CLI_RPM_BASE="stai-blockchain-cli-$STAI_INSTALLER_VERSION-1.$REDHAT_PLATFORM"
mkdir -p "dist/$CLI_RPM_BASE/opt/stai"
mkdir -p "dist/$CLI_RPM_BASE/usr/bin"
mkdir -p "dist/$CLI_RPM_BASE/etc/systemd/system"
cp -r dist/daemon/* "dist/$CLI_RPM_BASE/opt/stai/"
cp assets/systemd/*.service "dist/$CLI_RPM_BASE/etc/systemd/system/"

ln -s ../../opt/stai/stai "dist/$CLI_RPM_BASE/usr/bin/stai"
# This is built into the base build image
# shellcheck disable=SC1091
. /etc/profile.d/rvm.sh
rvm use ruby-3

export FPM_EDITOR="cat >dist/cli.spec <"

# /usr/lib64/libcrypt.so.1 is marked as a dependency specifically because newer versions of fedora bundle
# libcrypt.so.2 by default, and the libxcrypt-compat package needs to be installed for the other version
# Marking as a dependency allows yum/dnf to automatically install the libxcrypt-compat package as well
fpm -s dir -t rpm \
  --edit \
  -C "dist/$CLI_RPM_BASE" \
  --directories "/opt/stai" \
  -p "dist/$CLI_RPM_BASE.rpm" \
  --name stai-blockchain-cli \
  --license Apache-2.0 \
  --version "$STAI_INSTALLER_VERSION" \
  --architecture "$REDHAT_PLATFORM" \
  --description "Stai is a modern cryptocurrency built from scratch, designed to be efficient, decentralized, and secure." \
  --rpm-tag 'Recommends: libxcrypt-compat' \
  --rpm-tag '%define _build_id_links none' \
  --rpm-tag '%undefine _missing_build_ids_terminate_build' \
  --before-install=assets/rpm/before-install.sh \
  --rpm-tag 'Requires(pre): findutils' \
  .
# CLI only rpm done
cp -r dist/daemon ../stai-blockchain-gui/packages/gui
# Change to the gui package
cd ../stai-blockchain-gui/packages/gui || exit 1

# sets the version for stai-blockchain in package.json
cp package.json package.json.orig
jq --arg VER "$STAI_INSTALLER_VERSION" '.version=$VER' package.json > temp.json && mv temp.json package.json

export FPM_EDITOR="cat >../../../build_scripts/dist/gui.spec <"
jq '.rpm.fpm |= . + ["--edit"]' ../../../build_scripts/electron-builder.json > temp.json && mv temp.json ../../../build_scripts/electron-builder.json

echo "Building Linux(rpm) Electron app"
OPT_ARCH="--x64"
if [ "$REDHAT_PLATFORM" = "arm64" ]; then
  OPT_ARCH="--arm64"
fi
PRODUCT_NAME="stai"
echo npx electron-builder build --linux rpm "${OPT_ARCH}" \
  --config.extraMetadata.name=stai-blockchain \
  --config.productName="${PRODUCT_NAME}" --config.linux.desktop.Name="Stai Blockchain" \
  --config.rpm.packageName="stai-blockchain" \
  --config ../../../build_scripts/electron-builder.json
npx electron-builder build --linux rpm "${OPT_ARCH}" \
  --config.extraMetadata.name=stai-blockchain \
  --config.productName="${PRODUCT_NAME}" --config.linux.desktop.Name="Stai Blockchain" \
  --config.rpm.packageName="stai-blockchain" \
  --config ../../../build_scripts/electron-builder.json
LAST_EXIT_CODE=$?
ls -l dist/linux*-unpacked/resources

# reset the package.json to the original
mv package.json.orig package.json

if [ "$LAST_EXIT_CODE" -ne 0 ]; then
	echo >&2 "electron-builder failed!"
	exit $LAST_EXIT_CODE
fi

GUI_RPM_NAME="stai-blockchain-${STAI_INSTALLER_VERSION}-1.${REDHAT_PLATFORM}.rpm"
mv "dist/${PRODUCT_NAME}-${STAI_INSTALLER_VERSION}.rpm" "../../../build_scripts/dist/${GUI_RPM_NAME}"
cd ../../../build_scripts || exit 1

echo "Create final installer"
rm -rf final_installer
mkdir final_installer

mv "dist/${GUI_RPM_NAME}" final_installer/
# Move the cli only rpm into final installers as well, so it gets uploaded as an artifact
mv "dist/$CLI_RPM_BASE.rpm" final_installer/

ls -l final_installer/
