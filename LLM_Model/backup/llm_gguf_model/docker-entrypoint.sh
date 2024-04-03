#!/bin/bash

${FUNCTION_DIR}/llama.cpp/build/bin/server -m ${MODEL_PATH} -c ${CONTEXT_LENGTH} -ngl 100 --port 8081 & python3 sm_server_api.py