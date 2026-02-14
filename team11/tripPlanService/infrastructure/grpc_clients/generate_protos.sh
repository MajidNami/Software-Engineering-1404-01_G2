#!/bin/bash
# generate_protos.sh

# تبدیل .proto files به Python code

python -m grpc_tools.protoc \
    -I./protos \
    --python_out=. \
    --grpc_python_out=. \
    protos/facility.proto

python -m grpc_tools.protoc \
    -I./protos \
    --python_out=. \
    --grpc_python_out=. \
    protos/wiki.proto

python -m grpc_tools.protoc \
    -I./protos \
    --python_out=. \
    --grpc_python_out=. \
    protos/recom.proto

python -m grpc_tools.protoc \
    -I./protos \
    --python_out=. \
    --grpc_python_out=. \
    protos/trip.proto

echo "✅ Proto files generated!"