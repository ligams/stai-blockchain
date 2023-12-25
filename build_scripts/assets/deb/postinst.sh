#!/usr/bin/env bash
# Post install script for the UI .deb to place symlinks in places to allow the CLI to work similarly in both versions

set -e

ln -s /opt/stai/resources/app.asar.unpacked/daemon/stai /usr/bin/stai || true
ln -s /opt/stai/stai-blockchain /usr/bin/stai-blockchain || true
