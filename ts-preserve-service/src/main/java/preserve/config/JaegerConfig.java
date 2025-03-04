package preserve.config;

import io.opentracing.Tracer;
import io.opentracing.contrib.spring.web.client.TracingRestTemplateInterceptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.web.client.RestTemplate;

import javax.annotation.PostConstruct;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

@Configuration
public class JaegerConfig {

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private Tracer tracer;
    
    @Value("${opentracing.jaeger.probabilistic-sampler.sampling-rate:0.3}")
    private double samplingRate;

    @PostConstruct
    public void init() {
        List<ClientHttpRequestInterceptor> interceptors = new ArrayList<>(restTemplate.getInterceptors());
        interceptors.add(new TracingRestTemplateInterceptor(tracer));
        restTemplate.setInterceptors(interceptors);
        
        // Log the current configuration
        System.out.println("Jaeger tracing initialized with sampling rate: " + samplingRate);
    }
} 