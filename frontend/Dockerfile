# Dockerfile for React Frontend - Development
FROM node:18-alpine

WORKDIR /app

# Copy everything from frontend directory
COPY . .

# Install dependencies
RUN npm install

# Set API URL
ENV REACT_APP_API_URL=http://localhost:8000

# Expose port
EXPOSE 3000

# Run the development server
CMD ["npm", "start"]
