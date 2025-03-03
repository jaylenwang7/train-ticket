import cv2
import dlib
import base64
import numpy as np
import opentracing
from opentracing.ext import tags

path_save = "./images/"

# Get the global tracer
tracer = opentracing.global_tracer()

detector = dlib.get_frontal_face_detector()

def check(img):
    with tracer.start_active_span('face_detection') as scope:
        span = scope.span
        
        # Dlib 检测器
        with tracer.start_active_span('dlib_detector', child_of=span) as detector_scope:
            faces = detector(img, 1)
            detector_scope.span.set_tag('faces_found', len(faces))
            print("人脸数：", len(faces), "\n")

        if len(faces) < 1:
            span.set_tag('success', False)
            span.log_kv({'event': 'no face found'})
            return {"msg":"no human face found"}

        # 记录人脸矩阵大小
        height_max = 0
        width_sum = 0

        # 计算要生成的图像 img_blank 大小
        with tracer.start_active_span('process_face', child_of=span) as process_scope:
            for k, d in enumerate(faces):
                # 计算矩形大小
                # (x,y), (宽度width, 高度height)
                pos_start = tuple([d.left(), d.top()])
                pos_end = tuple([d.right(), d.bottom()])

                # 计算矩形框大小
                height = d.bottom() - d.top()
                width = d.right() - d.left()
                
                process_scope.span.set_tag('face_height', height)
                process_scope.span.set_tag('face_width', width)

                # 根据人脸大小生成空的图像
                img_blank = np.zeros((height, width, 3), np.uint8)

                for i in range(height):
                    for j in range(width):
                        img_blank[i][j] = img[d.top() + i][d.left() + j]

                print("Save to:", path_save + "img_face_" + str(k + 1) + ".jpg")
                cv2.imwrite(path_save + "img_face_" + str(k + 1) + ".jpg", img_blank)

                with tracer.start_active_span('encode_image', child_of=span) as encode_scope:
                    base64_str = cv2.imencode('.jpg',img_blank)[1].tostring()
                    base64_str = base64.b64encode(base64_str)
                    encode_scope.span.set_tag('encoded_size', len(base64_str))
                
                span.set_tag('success', True)
                return base64_str

