#!/bin/bash

# Quick start script for AI Travel Planner

echo "🌍 Starting AI Travel Planner..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/lib/python*/site-packages/streamlit" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Creating .env from example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your OpenAI API key!"
    echo "Then run this script again."
    exit 1
fi

# Run Streamlit
echo "🚀 Launching application..."
echo ""
cd src/ui
streamlit run app.py

