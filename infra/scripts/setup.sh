#!/bin/bash

# This script sets up the development environment for the plagiarism detector application.

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install Python and pip if not already installed
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip

# Install Ruby and Rails if not already installed
echo "Installing Ruby and Rails..."
sudo apt-get install -y ruby-full
gem install rails

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r ../backend/requirements.txt

# Install Ruby dependencies
echo "Installing Ruby dependencies..."
bundle install --gemfile=../frontend/Gemfile

# Run database migrations
echo "Running database migrations..."
cd ../frontend
rails db:migrate

echo "Setup complete!"