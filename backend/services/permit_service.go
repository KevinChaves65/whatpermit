package services

import (
	"context"
	"time"
	"whatpermit/database"
	"whatpermit/models"

	"go.mongodb.org/mongo-driver/bson"
)

func ResolvePermit(req models.PermitRequest) (models.Permit, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	filter := bson.M{
		"city":    req.City,
		"jobType": req.JobType,
	}

	var permit models.Permit

	err := database.PermitCollection.FindOne(ctx, filter).Decode(&permit)
	return permit, err
}
