# AI Shader Validator API Documentation

## Overview

The AI Shader Validator API provides comprehensive validation, analysis, and visualization capabilities for GLSL, ISF, and MadMapper shader formats. This RESTful API enables AI systems to validate, analyze, and self-correct shaders with visual analysis capabilities.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication for development purposes. In production, API keys or OAuth2 authentication will be implemented.

## Supported Shader Formats

- **GLSL**: OpenGL Shading Language (vertex and fragment shaders)
- **ISF**: Interactive Shader Format (JSON-based shader format)
- **MadMapper**: MadMapper shader format (comment-based metadata)

## API Endpoints

### Health Check

#### GET /health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### API Information

#### GET /info

Get information about the API and supported formats.

**Response:**
```json
{
  "name": "AI Shader Validator",
  "version": "1.0.0",
  "description": "Comprehensive shader validation and analysis API",
  "supported_formats": ["GLSL", "ISF", "MadMapper"],
  "features": [
    "syntax_validation",
    "semantic_analysis",
    "performance_analysis",
    "visualization",
    "error_correction"
  ]
}
```

### Configuration

#### GET /config

Get current API configuration.

**Response:**
```json
{
  "app_name": "AI Shader Validator",
  "app_version": "1.0.0",
  "debug": false,
  "log_level": "INFO",
  "max_shader_size": 1048576,
  "validation_timeout": 30,
  "default_image_width": 512,
  "default_image_height": 512
}
```

## Validation Endpoints

### Validate Shader

#### POST /validate

Validate a shader for syntax errors, semantic issues, and performance problems.

**Request Body:**
```json
{
  "shader_type": "GLSL",
  "shader_source": "#version 330 core\nuniform float time;\nout vec4 fragColor;\nvoid main() {\n    fragColor = vec4(1.0, 0.0, 0.0, 1.0);\n}",
  "parameters": {
    "time": 0.0
  },
  "options": {
    "strict_mode": false,
    "include_warnings": true,
    "performance_analysis": true
  }
}
```

**Response:**
```json
{
  "validation_result": {
    "is_valid": true,
    "errors": [],
    "warnings": [
      {
        "message": "Consider using precision qualifiers",
        "severity": "WARNING",
        "line": 1,
        "column": 1,
        "error_code": "PRECISION_WARNING"
      }
    ],
    "performance_metrics": {
      "texture_lookups": 0,
      "arithmetic_operations": 4,
      "conditional_statements": 0,
      "estimated_performance": "EXCELLENT"
    },
    "suggestions": [
      "Add precision qualifiers for better performance"
    ]
  },
  "processing_time": 0.125
}
```

### Batch Validation

#### POST /validate/batch

Validate multiple shaders in a single request.

**Request Body:**
```json
{
  "shaders": [
    {
      "id": "shader1",
      "shader_type": "GLSL",
      "shader_source": "#version 330 core\nvoid main() {\n    gl_FragColor = vec4(1.0);\n}"
    },
    {
      "id": "shader2",
      "shader_type": "ISF",
      "shader_source": "{\"ISFVersion\": \"2\", \"CODE\": [\"vec4 renderMain() { return vec4(1.0); }\"]}"
    }
  ],
  "options": {
    "parallel_processing": true,
    "include_warnings": true
  }
}
```

**Response:**
```json
{
  "results": {
    "shader1": {
      "is_valid": true,
      "errors": [],
      "warnings": []
    },
    "shader2": {
      "is_valid": true,
      "errors": [],
      "warnings": []
    }
  },
  "summary": {
    "total_shaders": 2,
    "valid_shaders": 2,
    "invalid_shaders": 0,
    "total_errors": 0,
    "total_warnings": 0,
    "processing_time": 0.250
  }
}
```

## Visualization Endpoints

### Generate Shader Image

#### POST /visualize

Generate an image from a shader.

**Request Body:**
```json
{
  "shader_type": "GLSL",
  "shader_source": "#version 330 core\nuniform float time;\nout vec4 fragColor;\nvoid main() {\n    vec2 uv = gl_FragCoord.xy / vec2(512.0, 512.0);\n    fragColor = vec4(uv.x, uv.y, sin(time), 1.0);\n}",
  "width": 512,
  "height": 512,
  "format": "PNG",
  "parameters": {
    "time": 0.0
  }
}
```

**Response:**
```json
{
  "image_id": "img_12345",
  "image_url": "/api/v1/images/img_12345",
  "metadata": {
    "width": 512,
    "height": 512,
    "format": "PNG",
    "size_bytes": 24576,
    "generation_time": 0.125
  }
}
```

### Get Image

#### GET /images/{image_id}

Retrieve a generated image.

**Response:** Binary image data with appropriate Content-Type header.

### Batch Visualization

#### POST /visualize/batch

Generate images for multiple shaders.

**Request Body:**
```json
{
  "requests": [
    {
      "id": "req1",
      "shader_type": "GLSL",
      "shader_source": "#version 330 core\nvoid main() {\n    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);\n}",
      "width": 256,
      "height": 256
    },
    {
      "id": "req2",
      "shader_type": "GLSL",
      "shader_source": "#version 330 core\nvoid main() {\n    gl_FragColor = vec4(0.0, 1.0, 0.0, 1.0);\n}",
      "width": 256,
      "height": 256
    }
  ],
  "format": "PNG"
}
```

**Response:**
```json
{
  "results": {
    "req1": {
      "image_id": "img_12346",
      "image_url": "/api/v1/images/img_12346",
      "success": true
    },
    "req2": {
      "image_id": "img_12347",
      "image_url": "/api/v1/images/img_12347",
      "success": true
    }
  },
  "summary": {
    "total_requests": 2,
    "successful": 2,
    "failed": 0,
    "processing_time": 0.500
  }
}
```

## Analysis Endpoints

### Analyze Shader

#### POST /analyze

Perform comprehensive analysis of a shader.

**Request Body:**
```json
{
  "shader_type": "GLSL",
  "shader_source": "#version 330 core\nuniform float time;\nout vec4 fragColor;\nvoid main() {\n    vec2 uv = gl_FragCoord.xy / vec2(512.0, 512.0);\n    fragColor = vec4(uv.x, uv.y, sin(time), 1.0);\n}",
  "analysis_types": [
    "performance",
    "complexity",
    "portability",
    "optimization"
  ]
}
```

**Response:**
```json
{
  "analysis_result": {
    "performance": {
      "score": 85,
      "texture_lookups": 0,
      "arithmetic_operations": 8,
      "conditional_statements": 0,
      "recommendations": [
        "Consider using precision qualifiers"
      ]
    },
    "complexity": {
      "cyclomatic_complexity": 1,
      "cognitive_complexity": 2,
      "maintainability_index": 95
    },
    "portability": {
      "glsl_version": "330",
      "compatible_platforms": ["OpenGL", "WebGL"],
      "potential_issues": []
    },
    "optimization": {
      "optimization_score": 80,
      "suggestions": [
        "Use const qualifiers where possible",
        "Consider loop unrolling for small loops"
      ]
    }
  },
  "processing_time": 0.250
}
```

### Error Visualization

#### POST /analyze/errors

Generate visual error reports for shader validation errors.

**Request Body:**
```json
{
  "shader_type": "GLSL",
  "shader_source": "#version 330 core\nvoid main() {\n    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0  // Missing semicolon\n}",
  "errors": [
    {
      "message": "Missing semicolon",
      "line": 3,
      "column": 35,
      "severity": "ERROR"
    }
  ]
}
```

**Response:**
```json
{
  "error_report_id": "err_12345",
  "error_report_url": "/api/v1/analysis/errors/err_12345",
  "metadata": {
    "total_errors": 1,
    "error_types": ["syntax"],
    "generation_time": 0.125
  }
}
```

## WebSocket Endpoints

### Real-time Validation

#### WebSocket /ws/validate

Real-time shader validation with progress updates.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/validate');
```

**Send validation request:**
```json
{
  "type": "validate",
  "shader_type": "GLSL",
  "shader_source": "#version 330 core\nvoid main() {\n    gl_FragColor = vec4(1.0);\n}"
}
```

**Receive progress updates:**
```json
{
  "type": "progress",
  "progress": 50,
  "message": "Analyzing shader syntax..."
}
```

**Receive final result:**
```json
{
  "type": "result",
  "validation_result": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  }
}
```

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Shader validation failed",
    "details": {
      "line": 5,
      "column": 10,
      "suggestion": "Add missing semicolon"
    }
  }
}
```

### Common Error Codes

- `INVALID_SHADER_TYPE`: Unsupported shader format
- `SYNTAX_ERROR`: Shader syntax errors
- `SEMANTIC_ERROR`: Shader semantic errors
- `VALIDATION_TIMEOUT`: Validation process timed out
- `RENDER_ERROR`: Error during shader rendering
- `INVALID_PARAMETERS`: Invalid request parameters
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Internal server error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **Validation endpoints**: 50 requests per minute per IP
- **Visualization endpoints**: 30 requests per minute per IP

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Response Headers

All responses include these headers:

- `Content-Type`: `application/json` for JSON responses
- `X-Request-ID`: Unique request identifier for tracking
- `X-Processing-Time`: Time taken to process the request
- `Cache-Control`: Caching directives for responses

## Examples

### Python Example

```python
import requests
import json

# Validate a GLSL shader
shader_source = """
#version 330 core
uniform float time;
out vec4 fragColor;
void main() {
    vec2 uv = gl_FragCoord.xy / vec2(512.0, 512.0);
    fragColor = vec4(uv.x, uv.y, sin(time), 1.0);
}
"""

response = requests.post(
    "http://localhost:8000/api/v1/validate",
    json={
        "shader_type": "GLSL",
        "shader_source": shader_source,
        "parameters": {"time": 0.0}
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Shader is valid: {result['validation_result']['is_valid']}")
    print(f"Errors: {len(result['validation_result']['errors'])}")
    print(f"Warnings: {len(result['validation_result']['warnings'])}")
else:
    print(f"Error: {response.json()}")
```

### JavaScript Example

```javascript
// Validate a shader
async function validateShader(shaderSource, shaderType = 'GLSL') {
    const response = await fetch('http://localhost:8000/api/v1/validate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            shader_type: shaderType,
            shader_source: shaderSource,
            parameters: { time: 0.0 }
        })
    });

    if (response.ok) {
        const result = await response.json();
        return result.validation_result;
    } else {
        throw new Error(`Validation failed: ${response.statusText}`);
    }
}

// Usage
const shader = `
#version 330 core
uniform float time;
out vec4 fragColor;
void main() {
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
`;

validateShader(shader)
    .then(result => {
        console.log('Validation result:', result);
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

## Support

For API support and questions:

- **Documentation**: [GitHub Wiki](https://github.com/your-repo/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@aishadervalidator.com

## Versioning

The API uses semantic versioning. The current version is v1.0.0.

- **Major version**: Breaking changes
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, backward compatible

## Changelog

### v1.0.0 (2024-01-01)
- Initial release
- GLSL, ISF, and MadMapper support
- Validation and visualization endpoints
- Real-time WebSocket support
- Comprehensive error reporting 