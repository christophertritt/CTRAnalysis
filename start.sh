#!/bin/bash
# Quick start script for Bellevue CTR Dashboard

set -e  # Exit on error

echo "🚌 Bellevue CTR Dashboard - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or later from https://www.python.org/"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Check if data file exists
if [ ! -f "CTR_Master_Dataset_2003-2025_CLEANED.csv" ]; then
    echo ""
    echo "⚠️  Warning: Data file not found"
    echo "Please ensure CTR_Master_Dataset_2003-2025_CLEANED.csv is in this directory"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ Data file found"
fi

# Run the dashboard
echo ""
echo "🚀 Starting dashboard..."
echo "   Press Ctrl+C to stop"
echo ""
streamlit run bellevue_ctr_dashboard_official_v3.py
