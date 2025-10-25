package main

import "github.com/gin-gonic/gin"

func main() {
	r := gin.Default()
	r.GET("/api1/health", func(ctx *gin.Context) {
		ctx.JSON(200, gin.H{"message": "Its OK!"})
	})
	r.Run("0.0.0.0:8080")
}
