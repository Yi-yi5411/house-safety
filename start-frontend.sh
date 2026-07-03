#!/bin/bash
# Start the uni-app frontend (H5 dev server)
# For WeChat Mini Program, use: npm run dev:mp-weixin

echo "Starting House Safety Assessment Frontend..."
cd "$(dirname "$0")/uniapp-house-safety"
npm install 2>/dev/null || echo "Dependencies already installed"
npm run dev:h5
