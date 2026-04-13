package main

import (
	"log"
	"whatpermit/database"
	"whatpermit/routes"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
)

func main() {
	app := fiber.New()
	app.Use(cors.New(cors.Config{
		AllowOrigins: "http://localhost:5173,http://localhost:5174",
		AllowMethods: "GET,POST,OPTIONS",
		AllowHeaders: "Origin, Content-Type, Accept",
	}))

	database.ConnectMongo()

	routes.SetupRoutes(app)

	log.Fatal(app.Listen(":8080"))
}
