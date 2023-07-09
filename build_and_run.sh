podman stop trade_news_backend
podman rm trade_news_backend
podman rmi localhost/trade_news_backend_newsfeed:latest
podman-compose up -d


