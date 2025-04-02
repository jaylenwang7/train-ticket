{{- define "opentelemetry_module.conf" -}}
NginxModuleEnabled {{ .Values.opentelemetry.enabled | default "ON" }};
NginxModuleOtelSpanExporter {{ .Values.opentelemetry.exporter | default "otlp" }};
NginxModuleOtelExporterEndpoint {{ .Values.opentelemetry.endpoint | default "opentelemetry-collector-deployment:4317" }};
NginxModuleServiceName {{ .Values.opentelemetry.serviceName | default "Gateway" }};
NginxModuleServiceNamespace {{ .Values.opentelemetry.serviceNamespace | default "Gateway" }};
NginxModuleServiceInstanceId {{ .Values.opentelemetry.serviceInstanceId | default "Nginx" }};
NginxModuleResolveBackends {{ .Values.opentelemetry.resolveBackends | default "ON" }};
NginxModuleTraceAsError {{ .Values.opentelemetry.traceAsError | default "OFF" }};
{{- end -}}