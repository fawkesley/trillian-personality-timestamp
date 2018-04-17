
code: venv/bin/activate protobuf/trillian_log_api.proto
	. venv/bin/activate; \
	python3 -m grpc_tools.protoc -I./protobuf --python_out=. --grpc_python_out=. \
	    protobuf/trillian_log_api.proto \
	    protobuf/trillian.proto \
	    protobuf/google/api/annotations.proto \
	    protobuf/google/api/http.proto \
	    protobuf/google/rpc/status.proto \
	    protobuf/crypto/keyspb/keyspb.proto \
	    protobuf/crypto/sigpb/sigpb.proto


venv/bin/activate:	requirements.txt
	virtualenv -p /usr/bin/python3 venv
	. venv/bin/activate; \
	pip install -r requirements.txt

.PHONY: run
run: code
	. venv/bin/activate; \
	FLASK_APP=app.py python3 -m flask run --host=0.0.0.0
