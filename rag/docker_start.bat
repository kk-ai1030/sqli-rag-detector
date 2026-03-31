@echo off
chcp 65001 >nul
echo 启动靶场...
docker start sqli-labs-8scenes
echo 访问 http://localhost:8080
start http://localhost:8080
echo 查看运行中的容器 docker ps
echo docker关闭命令 docker stop sqli-labs-8scenes
echo docker启动命令 docker start sqli-labs-8scenes
pause

