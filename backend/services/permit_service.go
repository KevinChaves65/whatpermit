package services

import (
	"context"
	"time"
	"whatpermit/database"
	"whatpermit/models"

	"go.mongodb.org/mongo-driver/bson"
)

func ResolvePermit(req models.PermitRequest) (models.PermitResponse, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	filter := bson.M{
		"city":    req.City,
		"jobType": req.JobType,
	}

	var permit models.Permit
	err := database.PermitCollection.FindOne(ctx, filter).Decode(&permit)
	if err != nil {
		return models.PermitResponse{}, err
	}

	response := models.PermitResponse{
		PermitRequired: permit.PermitRequired,
		PermitName:     permit.PermitName,
		Description:    permit.Description,
		Conditions:     permit.Conditions,
		PermitTypes:    permit.PermitTypes,
		Cost:           permit.Cost,
		CostNotes:      permit.CostNotes,
		Documents:      permit.Documents,
		ZoningRules:    permit.ZoningRules,
		Notes:          permit.Notes,
		Source: models.Source{
			Authority:      permit.Authority,
			AuthorityLevel: permit.AuthorityLevel,
			Section:        permit.Section,
			BylawReference: permit.BylawReference,
			URL:            permit.URL,
		},
	}

	return response, nil
}
