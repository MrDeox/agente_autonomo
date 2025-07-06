
# Enhanced API Documentation

## Available Endpoints


### Enhanced Cache Stats
- **Method**: GET
- **Path**: /enhanced/cache/stats
- **Description**: Get enhanced cache statistics

### Enhanced Monitor Metrics
- **Method**: GET
- **Path**: /enhanced/monitor/metrics
- **Description**: Get enhanced monitoring metrics

### Enhanced Validator
- **Method**: POST
- **Path**: /enhanced/validator/validate
- **Description**: Run enhanced validation


## Usage Examples


```bash
# Example API calls
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"target": "agent/"}'
```

