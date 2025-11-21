package models

type Permit struct {
	City           string   `json:"city" bson:"city"`
	JobType        string   `json:"jobType" bson:"jobType"`
	PermitRequired bool     `json:"permitRequired" bson:"permitRequired"`
	PermitName     string   `json:"permitName" bson:"permitName"`
	Cost           int      `json:"cost" bson:"cost"`
	Documents      []string `json:"documents" bson:"documents"`
	Authority      string   `json:"authority" bson:"authority"`
	Section        string   `json:"section" bson:"section"`
	URL            string   `json:"url" bson:"url"`
}

type PermitRequest struct {
	PostalCode string `json:"postal_code"`
	City       string `json:"city"`
	JobType    string `json:"job_type"`
}

type PermitResponse struct {
	PermitRequired bool     `json:"permitRequired"`
	PermitName     string   `json:"permitName"`
	Cost           int      `json:"cost"`
	Documents      []string `json:"documents"`
	Source         Source   `json:"source"`
}

type Source struct {
	Authority string `json:"authority"`
	Section   string `json:"section"`
	URL       string `json:"url"`
}
