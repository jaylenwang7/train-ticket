{{- define "nginx.conf" -}}
load_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/1.23.1/ngx_http_opentelemetry_module.so;
worker_processes  1;
error_log error.log {{ .Values.nginx.errorLogLevel | default "warn" }};

events {
  worker_connections 1024;
}

http {
  include mime.types;
  default_type  application/octet-stream;

  sendfile        on;
  keepalive_timeout  65;

  include /etc/nginx/conf.d/*.conf;
}
{{- end -}}