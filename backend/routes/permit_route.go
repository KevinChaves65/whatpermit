package routes

import (
	"whatpermit/controllers"

	"github.com/gofiber/fiber/v2"
)

func SetupRoutes(app *fiber.App) {
	api := app.Group("/api")

	api.Post("/permit/check", controllers.CheckPermit)
}
