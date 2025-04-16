package adminbasic;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.integration.annotation.IntegrationComponentScan;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.web.client.RestTemplate;
import springfox.documentation.swagger2.annotations.EnableSwagger2;
import org.springframework.beans.factory.annotation.Value;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @author fdse
 */
@SpringBootApplication
@EnableAspectJAutoProxy(proxyTargetClass = true)
@EnableAsync
@IntegrationComponentScan
@EnableSwagger2
public class AdminBasicInfoApplication {

    public static void main(String[] args) {
        SpringApplication.run(AdminBasicInfoApplication.class, args);
    }

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        // Get timeout values from configuration
        int connectTimeout = connectTimeoutValue; // Use the @Value injected property
        int readTimeout = readTimeoutValue; // Use the @Value injected property
        
        // Log the timeout values
        logger.info("Configuring RestTemplate with connectTimeout: {} ms, readTimeout: {} ms", 
                    connectTimeout, readTimeout);
        
        return builder
            .setConnectTimeout(Duration.ofMillis(connectTimeout))
            .setReadTimeout(Duration.ofMillis(readTimeout))
            .build();
    }

    // Add a logger for the class
    private static final Logger logger = LoggerFactory.getLogger(AdminBasicInfoApplication.class);

    // Inject the timeout values
    @Value("${spring.rest.template.connection-timeout:30000}")
    private int connectTimeoutValue;

    @Value("${spring.rest.template.read-timeout:30000}")
    private int readTimeoutValue;
}
