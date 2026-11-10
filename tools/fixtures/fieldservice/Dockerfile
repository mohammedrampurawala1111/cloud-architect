FROM node:22-alpine AS build
WORKDIR /app
COPY . .
RUN npm ci && npx prisma generate && npx tsc

FROM node:22-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
