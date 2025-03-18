uv sync
source .venv/bin/activate
deactivate


uv run fastapi dev 



curl -X POST \
--cert ./security/vespa-cert.pem \
--key ./security/vespa-key.pem \
--cacert ./security/clients.pem \
-H "Content-Type: application/json" \
-d '{
"fields": {
"title": 1
}
}' \
https://aa8f0aa2.b1ccdfef.z.vespa-app.cloud/document/v1/ddoc/ddoc/docid/1


