# Multi-stage build for frontend

# Development stage
FROM node:18 as development

WORKDIR /app

COPY package*.json ./

RUN npm ci --silent

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage
FROM node:18 as build

WORKDIR /app

COPY package*.json ./

RUN npm ci --silent

COPY . .

RUN npm run type-check
RUN npm run build

# Production stage
FROM node:18-slim as production

WORKDIR /app

RUN npm install -g serve

COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["serve", "-s", "dist", "-l", "3000"]
