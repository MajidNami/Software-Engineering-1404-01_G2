# team8/frontend/Dockerfile

# build stage
FROM node:20-alpine AS build
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci || npm install

COPY . .

# Build with base=/team8/ so assets resolve behind the gateway path
RUN npm run build -- --base=/team8/

# serve stage
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Put the build output under /team8/
COPY --from=build /app/dist /usr/share/nginx/html/team8

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

