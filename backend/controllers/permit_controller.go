package controllers

import (
	"fmt"
	"whatpermit/models"
	"whatpermit/services"

	"github.com/gofiber/fiber/v2"
	"go.mongodb.org/mongo-driver/mongo"
)

func CheckPermit(c *fiber.Ctx) error {
	var req models.PermitRequest

	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Invalid input"})
	}

	if req.City == "" || req.JobType == "" {
		return c.Status(400).JSON(fiber.Map{"error": "city and job_type are required"})
	}

	results, err := services.ResolvePermits(req)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return c.Status(404).JSON(fiber.Map{
				"error": "No permit rules found for this city and project type",
			})
		}
		fmt.Printf("ResolvePermits error: %v\n", err)
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}

	return c.JSON(fiber.Map{
		"city":    req.City,
		"jobType": req.JobType,
		"rules":   results,
	})
}
