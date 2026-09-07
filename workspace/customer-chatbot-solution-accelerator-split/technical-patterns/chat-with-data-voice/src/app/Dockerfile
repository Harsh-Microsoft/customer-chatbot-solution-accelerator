# Ported from scenario-app/frontend/Dockerfile (plan row 38), collapsed to a
# single build context since the widget (chat-app/frontend) and host app
# (scenario-app/frontend) now live in one package (plan section 4.8).
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build
RUN cp dist/widget/widget.js dist/widget.js

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html

RUN mkdir -p /etc/nginx/conf.d && touch /etc/nginx/conf.d/api-proxy.conf

COPY public/startup.sh /docker-entrypoint.d/startup.sh
RUN chmod +x /docker-entrypoint.d/startup.sh && sed -i 's/\r$//' /docker-entrypoint.d/startup.sh
EXPOSE 80
CMD ["/bin/sh", "-c", "/docker-entrypoint.d/startup.sh"]
