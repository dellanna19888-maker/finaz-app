# finaz-app – Container-Image (Frontend-Build + API/Compliance-Backend in einem)
FROM node:22-slim

WORKDIR /app

# Abhängigkeiten (inkl. devDeps, da Build-Tools wie vite/tsx benötigt werden)
COPY package*.json ./
RUN npm ci --include=dev

# Quellcode + Build
COPY . .
RUN npm run build

ENV NODE_ENV=production
# Der Server nutzt process.env.PORT (Fallback 3001) und liefert dist/ + /api aus.
EXPOSE 3001

CMD ["npm", "run", "api"]
