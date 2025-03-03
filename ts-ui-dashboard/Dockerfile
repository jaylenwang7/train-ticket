FROM nginx:1.23.1

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
RUN apt-get update && apt-get install -y git cmake build-essential libpcre3-dev zlib1g-dev

# Install OpenTracing module for Nginx
RUN cd /tmp && \
    git clone -b v0.10.0 https://github.com/opentracing-contrib/nginx-opentracing.git && \
    cd nginx-opentracing && \
    wget -O - https://github.com/jaegertracing/jaeger-client-cpp/archive/v0.7.0.tar.gz | tar -zxf - && \
    mkdir -p jaeger-client-cpp-0.7.0/build && \
    cd jaeger-client-cpp-0.7.0/build && \
    cmake -DCMAKE_BUILD_TYPE=Release \
          -DJAEGERTRACING_PLUGIN=ON \
          -DBUILD_TESTING=OFF .. && \
    make && make install

COPY opentracing_module.conf /etc/nginx/conf.d
COPY server.conf /etc/nginx/conf.d
COPY static /usr/share/nginx/html
COPY docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]