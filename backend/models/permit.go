package models

// ZoningRules holds structured dimensional and land-use rules for a permit type.
type ZoningRules struct {
	MaxHeightM              float64  `json:"maxHeightM,omitempty" bson:"maxHeightM,omitempty"`
	MaxHeightAboveGradeM    float64  `json:"maxHeightAboveGradeM,omitempty" bson:"maxHeightAboveGradeM,omitempty"`
	SetbackFrontYardM       float64  `json:"setbackFrontYardM,omitempty" bson:"setbackFrontYardM,omitempty"`
	SetbackRearYardM        float64  `json:"setbackRearYardM,omitempty" bson:"setbackRearYardM,omitempty"`
	SetbackSideYardM        float64  `json:"setbackSideYardM,omitempty" bson:"setbackSideYardM,omitempty"`
	LotCoverageMaxPercent   float64  `json:"lotCoverageMaxPercent,omitempty" bson:"lotCoverageMaxPercent,omitempty"`
	MaxAreaM2               float64  `json:"maxAreaM2,omitempty" bson:"maxAreaM2,omitempty"`
	MinCeilingHeightM       float64  `json:"minCeilingHeightM,omitempty" bson:"minCeilingHeightM,omitempty"`
	MaxHeightFrontYardM     float64  `json:"maxHeightFrontYardM,omitempty" bson:"maxHeightFrontYardM,omitempty"`
	MaxHeightSideRearYardM  float64  `json:"maxHeightSideRearYardM,omitempty" bson:"maxHeightSideRearYardM,omitempty"`
	Notes                   string   `json:"notes,omitempty" bson:"notes,omitempty"`
}

// LiveLink is a URL + title pair collected by the live scraper.
type LiveLink struct {
	Title string `json:"title" bson:"title"`
	URL   string `json:"url" bson:"url"`
}

// Permit is the canonical document stored in MongoDB and served by the API.
type Permit struct {
	City            string      `json:"city" bson:"city"`
	JobType         string      `json:"jobType" bson:"jobType"`
	RuleID          string      `json:"ruleId,omitempty" bson:"ruleId,omitempty"`
	PermitRequired  bool        `json:"permitRequired" bson:"permitRequired"`
	PermitName      string      `json:"permitName" bson:"permitName"`
	Description     string      `json:"description,omitempty" bson:"description,omitempty"`
	Conditions      []string    `json:"conditions,omitempty" bson:"conditions,omitempty"`
	PermitTypes     []string    `json:"permitTypes,omitempty" bson:"permitTypes,omitempty"`
	Keywords        []string    `json:"keywords,omitempty" bson:"keywords,omitempty"`
	Cost            float64     `json:"cost" bson:"cost"`
	CostNotes       string      `json:"costNotes,omitempty" bson:"costNotes,omitempty"`
	Documents       []string    `json:"documents" bson:"documents"`
	ZoningRules     ZoningRules `json:"zoningRules,omitempty" bson:"zoningRules,omitempty"`
	Authority       string      `json:"authority" bson:"authority"`
	AuthorityLevel  string      `json:"authorityLevel" bson:"authorityLevel"`
	Section         string      `json:"section" bson:"section"`
	BylawReference  string      `json:"bylawReference,omitempty" bson:"bylawReference,omitempty"`
	URL             string      `json:"url" bson:"url"`
	FeesURL         string      `json:"feesUrl,omitempty" bson:"feesUrl,omitempty"`
	Notes           string      `json:"notes,omitempty" bson:"notes,omitempty"`
	LivePermitLinks []LiveLink  `json:"livePermitLinks,omitempty" bson:"livePermitLinks,omitempty"`
	LiveZoningLinks []LiveLink  `json:"liveZoningLinks,omitempty" bson:"liveZoningLinks,omitempty"`
}

// PermitRequest is the incoming query from the frontend.
type PermitRequest struct {
	City    string `json:"city"`
	JobType string `json:"job_type"`
}

// PermitResponse is what the API returns to the frontend.
type PermitResponse struct {
	PermitRequired bool        `json:"permitRequired"`
	PermitName     string      `json:"permitName"`
	Description    string      `json:"description,omitempty"`
	Conditions     []string    `json:"conditions,omitempty"`
	PermitTypes    []string    `json:"permitTypes,omitempty"`
	Cost           float64     `json:"cost"`
	CostNotes      string      `json:"costNotes,omitempty"`
	Documents      []string    `json:"documents"`
	ZoningRules    ZoningRules `json:"zoningRules,omitempty"`
	Notes          string      `json:"notes,omitempty"`
	Source         Source      `json:"source"`
}

// Source identifies the authority and legal reference for a permit requirement.
type Source struct {
	Authority      string `json:"authority"`
	AuthorityLevel string `json:"authorityLevel"`
	Section        string `json:"section"`
	BylawReference string `json:"bylawReference,omitempty"`
	URL            string `json:"url"`
}
