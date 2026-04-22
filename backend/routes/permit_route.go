package routes

import (
	"whatpermit/controllers"

	"github.com/gofiber/fiber/v2"
)

func SetupRoutes(app *fiber.App) {
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.SendString("ok")
	})

	api := app.Group("/api")
	api.Post("/permit/check", controllers.CheckPermit)
}
