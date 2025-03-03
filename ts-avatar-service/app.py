from flask import Flask, request, jsonify
import numpy as np
import urllib
import cv2
import os
import json
import base64
import traceback
from face_detect import check
from jaeger_client import Config
import flask_opentracing
import opentracing
from opentracing.ext import tags

app = Flask(__name__)

# Configure Jaeger tracer
def init_tracer():
    jaeger_host = os.getenv("JAEGER_AGENT_HOST", "jaeger")
    jaeger_port = os.getenv("JAEGER_AGENT_PORT", "6831")
    
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
            'local_agent': {
                'reporting_host': jaeger_host,
                'reporting_port': int(jaeger_port),
            },
        },
        service_name='ts-avatar-service',
    )
    return config.initialize_tracer()

# Initialize tracer
tracer = init_tracer()

# Initialize Flask OpenTracing extension
flask_opentracing.init_tracing(tracer)

# TODO:
# ~~1. 获取图片~~
#  ~2. 检测图片是否ok
#  ~3. 人脸检测&切割
#  ~4. 返回base64格式的图片
# 5. 前端传文件
# 6. Dockerfile部署

receive_path = r"./received/"


@app.route('/api/v1/avatar', methods=["POST"])
def hello():
    with tracer.start_active_span('process_avatar') as scope:
        span = scope.span
        span.set_tag(tags.HTTP_METHOD, request.method)
        span.set_tag(tags.HTTP_URL, request.url)
        
        # receive file
        with tracer.start_active_span('decode_request', child_of=span) as decode_scope:
            data = request.get_data().decode('utf-8')
            data = json.loads(data)
            image_b64 = data.get("img")
            if image_b64 is None or len(image_b64) < 1:
                decode_scope.span.set_tag('error', True)
                decode_scope.span.log_kv({'event': 'error', 'message': 'missing img in request'})
                return jsonify({"msg": "need img in request body"}), 400

        try:
            with tracer.start_active_span('process_image', child_of=span) as process_scope:
                process_scope.span.log_kv({'event': 'processing image', 'image_size': len(image_b64)})
                
                image_decode = base64.b64decode(image_b64)
                nparr = np.fromstring(image_decode, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                with tracer.start_active_span('face_detection', child_of=process_scope.span) as face_scope:
                    result = check(image)
                    if type(result) == dict and result.get("msg") is not None:
                        face_scope.span.set_tag('face_detected', False)
                        face_scope.span.log_kv({'event': 'no face detected'})
                    else:
                        face_scope.span.set_tag('face_detected', True)
                        face_scope.span.log_kv({'event': 'face detected'})
                
        except Exception as e:
            span.set_tag('error', True)
            span.log_kv({
                'event': 'error',
                'error.kind': str(type(e)),
                'error.object': str(e),
                'error.stack': traceback.format_exc()
            })
            return jsonify({"msg": "exception:" + str(traceback.format_exc())}), 500

        if type(result) == dict and result.get("msg") is not None:
            return jsonify(result), 400

        return result, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
