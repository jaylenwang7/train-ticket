package main

import (
	"github.com/gin-gonic/gin"
	"github.com/opentracing/opentracing-go"
	"github.com/uber/jaeger-client-go"
	jaegercfg "github.com/uber/jaeger-client-go/config"
	"log"
	"net/http"
)

type News struct {
	Title   string `json:"Title"`
	Content string `json:"Content"`
}

func initJaeger() {
	cfg := jaegercfg.Configuration{
		ServiceName: "ts-news-service",
		Sampler: &jaegercfg.SamplerConfig{
			Type:  jaeger.SamplerTypeConst,
			Param: 1,
		},
		Reporter: &jaegercfg.ReporterConfig{
			LogSpans:           true,
			LocalAgentHostPort: "jaeger:6831",
		},
	}

	tracer, _, err := cfg.NewTracer()
	if err != nil {
		log.Fatalf("Could not initialize jaeger tracer: %s", err.Error())
	}
	opentracing.SetGlobalTracer(tracer)
}

func tracingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		spanCtx, _ := opentracing.StartSpanFromContext(c.Request.Context(), c.Request.URL.Path)
		defer spanCtx.Finish()
		c.Next()
	}
}

func main() {
	initJaeger()
	r := gin.Default()
	r.Use(tracingMiddleware())

	r.GET("/hello", func(c *gin.Context) {
		c.String(200, "Hello, World!")
	})

	r.GET("/news-service/news", func(c *gin.Context) {
		newsList := []News{
			{Title: "News Title 1", Content: "News Content 1"},
			{Title: "News Title 2", Content: "News Content 2"},
		}
		c.JSON(http.StatusOK, newsList)
	})

	r.Run()
}
