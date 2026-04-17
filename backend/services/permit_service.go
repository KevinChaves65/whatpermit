package services

import (
	"context"
	"time"
	"whatpermit/database"
	"whatpermit/models"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

func ResolvePermits(req models.PermitRequest) ([]models.PermitResponse, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	filter := bson.M{
		"city":    req.City,
		"jobType": req.JobType,
	}

	cursor, err := database.PermitCollection.Find(ctx, filter)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var results []models.PermitResponse

	for cursor.Next(ctx) {
		var permit models.Permit
		if err := cursor.Decode(&permit); err != nil {
			continue
		}

		results = append(results, models.PermitResponse{
			RuleID:         permit.RuleID,
			PermitRequired: permit.PermitRequired,
			PermitName:     permit.PermitName,
			Description:    permit.Description,
			Conditions:     permit.Conditions,
			PermitTypes:    permit.PermitTypes,
			Fee:            permit.Fee,
			Cost:           permit.Cost,
			CostNotes:      permit.CostNotes,
			Documents:      permit.Documents,
			RequiredForms:  permit.RequiredForms,
			ZoningRules:    permit.ZoningRules,
			Notes:          permit.Notes,
			ApplyOnlineURL: permit.ApplyOnlineURL,
			Source: models.Source{
				Authority:      permit.Authority,
				AuthorityLevel: permit.AuthorityLevel,
				Section:        permit.Section,
				BylawReference: permit.BylawReference,
				URL:            permit.URL,
			},
		})
	}

	if err := cursor.Err(); err != nil {
		return nil, err
	}

	if len(results) == 0 {
		return nil, mongo.ErrNoDocuments
	}

	return results, nil
}
