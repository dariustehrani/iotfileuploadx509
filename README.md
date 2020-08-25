

````
docker run -v `pwd`/certs:/certs -e X509_CERT_FILE=/certs/fullchain.cert.pem -e X509_KEY_FILE=/certs/new-device.key.pem --env-file ./env.list -it iotfile:v3 /bin/bash
````

````
python /pythoniot/sample.py 
````

## Related documents
https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-python-python-file-upload
https://github.com/Azure/azure-iot-sdk-python/blob/master/azure-iot-device/samples/async-hub-scenarios/receive_message_x509.py 