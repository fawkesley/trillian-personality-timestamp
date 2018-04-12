code: venv/bin/activate protobuf/trillian_log_api.proto
	. venv/bin/activate; \
	python -m grpc_tools.protoc -I./protobuf --python_out=. --grpc_python_out=. protobuf/trillian_log_api.proto


venv/bin/activate:	requirements.txt
	virtualenv venv
	. venv/bin/activate; \
	pip install -r requirements.txt
