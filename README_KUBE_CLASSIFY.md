# Deploying TensorFlow Models to Kubernetes on the IBM Cloud

As documented in [Image Recognition with Tensorflow classification on OpenWhisk](https://ansi.23-5.eu/2017/11/image-recognition-tensorflow-classification-openwhisk/) the MobileNet model can be used to classify images in OpenWhisk functions. The same Docker image can also be deployed to Kubernetes on the IBM Cloud. This is useful when models are too big to be deployed to OpenWhisk, for example the Inception model rather than MobileNet.

Before the Docker image can be built, you need to create an instance of IBM Object Storage on the IBM Cloud. Check out the article [Accessing IBM Object Store from Python](https://ansi.23-5.eu/2017/11/accessing-ibm-object-store-python/) for details. Paste the values of 'region', 'projectId', 'userId' and 'password' in [classifier.py](Classify/classifier.py).

After this upload the model (retrained_graph.pb and retrained_labels.txt) into your Object Storage instance in a bucket 'tensorflow'.

In order to build the image, run these commands:

```sh
$ cd Classify
$ docker build -t $USER/tensorflow-kubernetes-classify:latest .
```

In order to test the image, run these commands:

```sh
$ docker run -d -p 8080:8080 $USER/tensorflow-kubernetes-classify:latest
$ curl http://localhost:8080/classify?image-url=http://heidloff.net/wp-content/uploads/2017/10/codetalks17-6.jpg
```

In order to deploy the image to Kubernetes, run the following commands after you've updated your user name in [tensorflow-model-classifier.yaml](Classify/tensorflow-model-classifier.yaml):

```sh
$ docker push $USER/tensorflow-kubernetes-classify:latest
$ bx plugin install container-service -r Bluemix
$ bx login -a https://api.eu-de.bluemix.net
$ bx cs cluster-config mycluster
$ export KUBECONFIG=/Users/nheidlo.....
$ cd Classify
$ kubectl create -f tensorflow-model-classifier.yaml
$ bx cs workers mycluster
$ kubectl describe service classifier-service
```

In order to test the classifier, open the following URL after you've replaced your 'Public IP' and 'NodePort' from the previous two commands:

http://169.51.19.8:32441/classify?image-url=http://heidloff.net/wp-content/uploads/2017/10/codetalks17-6.jpg