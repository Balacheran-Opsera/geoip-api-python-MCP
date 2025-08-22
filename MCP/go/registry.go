package main

import (
	"github.com/geographic-api/mcp-server/config"
	"github.com/geographic-api/mcp-server/models"
	tools_events "github.com/geographic-api/mcp-server/tools/events"
)

func GetAll(cfg *config.APIConfig) []models.Tool {
	return []models.Tool{
		tools_events.CreateGet_query_jsonTool(cfg),
	}
}
