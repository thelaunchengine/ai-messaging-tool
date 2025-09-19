#!/bin/bash
# Simple health check script for ECS
curl -f http://localhost:8001/api/health || exit 1
