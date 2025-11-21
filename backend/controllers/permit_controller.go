package controllers

import (
	"whatpermit/models"
	"whatpermit/services"

	"github.com/gofiber/fiber/v2"
)

func CheckPermit(c *fiber.Ctx) error {
	var req models.PermitRequest

	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Invalid input"})
	}

	result, err := services.ResolvePermit(req)

	if err != nil {
		return c.Status(404).JSON(fiber.Map{
			"error": "Permit not found for this project type",
		})
	}

	return c.JSON(result)
}
