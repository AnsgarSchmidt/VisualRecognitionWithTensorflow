import os
import flask
import base64
import numpy               as     np
import tensorflow          as     tf
from   swiftclient.service import Connection
import urllib.request

app       = flask.Flask(__name__)
app.debug = False
graph     = tf.Graph()
labels    = []
modelNeedsToBeLoaded = True

@app.route('/classify', methods=['GET'])
def classify():
    global modelNeedsToBeLoaded
    try:
        if (modelNeedsToBeLoaded == True):
            modelNeedsToBeLoaded = False
            init()            

        imageUrl = flask.request.args.get('image-url', '')
        file_name, headers = urllib.request.urlretrieve(imageUrl)
        file_reader = tf.read_file(file_name, "file_reader")

    except Exception as err:
        response = flask.jsonify({'error': 'Issue with Object Storage credentials or with image URL'})
        response.status_code = 400
        return response
    
    image_reader     = tf.image.decode_jpeg(file_reader, channels=3, name='jpeg_reader')
    float_caster     = tf.cast(image_reader, tf.float32)
    dims_expander    = tf.expand_dims(float_caster, 0)
    resized          = tf.image.resize_bilinear(dims_expander, [224, 224])
    normalized       = tf.divide(tf.subtract(resized, [128]), [128])
    input_operation  = graph.get_operation_by_name("import/input")
    output_operation = graph.get_operation_by_name("import/final_result")
    tf_picture       = tf.Session().run(normalized)

    with tf.Session(graph=graph) as sess:
        results = np.squeeze(sess.run(output_operation.outputs[0], {input_operation.outputs[0]: tf_picture}))
        index   = results.argsort()
        answer  = {}

        for i in index:
            answer[labels[i]] = float(results[i])

        response = flask.jsonify(answer)
        response.status_code = 200

    return response

@app.route('/init', methods=['POST'])
def init():
    try:

        message = flask.request.get_json(force=True, silent=True)

        if message and not isinstance(message, dict):
            flask.abort(404)

        conn = Connection(key='xxxxx',
                          authurl='https://identity.open.softlayer.com/v3',
                          auth_version='3',
                          os_options={"project_id": 'xxxxxx',
                                      "user_id": 'xxxxxx',
                                      "region_name": 'dallas'}
                          )

        obj       = conn.get_object("tensorflow", "retrained_graph.pb")
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(obj[1])
        with graph.as_default():
            tf.import_graph_def(graph_def)

        obj    = conn.get_object("tensorflow", "retrained_labels.txt")
        for i in obj[1].decode("utf-8").split():
            labels.append(i)

    except Exception as e:
        print("Error in downloading content")
        print(e)
        response = flask.jsonify({'error downloading models': e})
        response.status_code = 512

    return ('OK', 200)


@app.route('/run', methods=['POST'])
def run():

    def error():
        response = flask.jsonify({'error': 'The action did not receive a dictionary as an argument.'})
        response.status_code = 404
        return response

    message = flask.request.get_json(force=True, silent=True)

    if message and not isinstance(message, dict):
        return error()
    else:
        args = message.get('value', {}) if message else {}

        if not isinstance(args, dict):
            return error()

        print(args)

        if "payload" not in args:
            return error()

        print("=====================================")
        with open("/test.jpg", "wb") as f:
            f.write(base64.b64decode(args['payload']))

        file_reader      = tf.read_file("/test.jpg", "file_reader")
        #file_reader      = tf.decode_base64(args['payload'])
        image_reader     = tf.image.decode_jpeg(file_reader, channels=3, name='jpeg_reader')
        float_caster     = tf.cast(image_reader, tf.float32)
        dims_expander    = tf.expand_dims(float_caster, 0)
        resized          = tf.image.resize_bilinear(dims_expander, [224, 224])
        normalized       = tf.divide(tf.subtract(resized, [128]), [128])
        input_operation  = graph.get_operation_by_name("import/input")
        output_operation = graph.get_operation_by_name("import/final_result")
        tf_picture       = tf.Session().run(normalized)

        with tf.Session(graph=graph) as sess:
            results = np.squeeze(sess.run(output_operation.outputs[0], {input_operation.outputs[0]: tf_picture}))
            index   = results.argsort()
            answer  = {}

            for i in index:
                answer[labels[i]] = float(results[i])

            response = flask.jsonify(answer)
            response.status_code = 200

    return response


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PROXY_PORT', 8080))
    app.run(host='0.0.0.0', port=port)
