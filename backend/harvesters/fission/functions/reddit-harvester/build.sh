#!/bin/sh
# python3 -m pip install --upgrade pip
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# pip install sentence_transformers --extra-index-url https://download.pytorch.org/whl/cpu
python3 -m pip install -r ${SRC_PKG}/requirements.txt -t ${SRC_PKG} && cp -r ${SRC_PKG} ${DEPLOY_PKG}
# python3 ${SRC_PKG}/download_models.py