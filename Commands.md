Train

docker build -t ansi/tensorflow-openwhisk-trainer:latest .
docker run --rm ansi/tensorflow-openwhisk-trainer:latest
docker push     ansi/tensorflow-openwhisk-trainer:latest

kubectl apply -f train.yml


Classify
docker build -t ansi/tensorflow-openwhisk-classify:latest .
docker run -it  --rm ansi/tensorflow-openwhisk-classify:latest /bin/bash
docker push     ansi/tensorflow-openwhisk-classify:latest

wsk action delete tensorflow-classify
wsk action create tensorflow-classify --docker ansi/tensorflow-openwhisk-classify:dev -a {"a": "s"}
wsk action get    tensorflow-classift --url

wsk action invoke --result tensorflow-classify --param payload `cat host/Downloads/test.base64` --param otto walkes

wsk activation list
wsk activation poll
wsk activation get 

wsk activation logs `wsk activation list | grep tensorflow-classify | cut -f 1 -d " " |head -n 1`
