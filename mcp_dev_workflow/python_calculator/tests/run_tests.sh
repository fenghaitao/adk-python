#!/bin/bash
# Run tests with the PYTHONPATH environment variable set
PYTHONPATH=../src pytest --cov=. --cov-report=term-missing