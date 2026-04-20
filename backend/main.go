package main

import (
	"log"
	"os"
	"whatpermit/database"
	"whatpermit/routes"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
)

func main() {
	app := fiber.New()
	app.Use(cors.New(cors.Config{
		AllowOrigins: "http://localhost:5173,http://localhost:5174,http://localhost:5175,https://whatpermit.ca,https://www.whatpermit.ca,https://whatpermit.onrender.com,https://whatpermit-backend.onrender.com",
		AllowMethods: "GET,POST,OPTIONS",
		AllowHeaders: "Origin, Content-Type, Accept",
	}))

	database.ConnectMongo()

	routes.SetupRoutes(app)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Fatal(app.Listen(":" + port))
}
