# dockerのインストール
``` terminal
sudo apt update
sudo apt install docker.io docker-compose

docker --version
docker compose version

sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

# MariaDB公式イメージの取得
``` terminal
docker pull mariadb:latest
```

# ボリュームコンテナの作成
``` terminal
docker volume create inspection_mariadb_data
docker volume ls

docker run --rm \
 -v inspection_mariadb_data:/target \
 -v "$(pwd)":/backup \
 alpine \
 tar xvf /backup/mariadb_data.tar.gz -C /target

docker run --rm -v inspection_data:/data:ro alpine ls -la /data
```

# Composeファイルの作成
``` Compose.yaml
services:
	mariadb:
		image: mariadb:11.4
		container_name: inspection-mariadb
	
		enviroment:
			MARIADB_ROOT_PASSWORD: root
	
		ports:
			- "3306:3306"
	
		volumes:
			- inspection_mariadb_data:/var/lib/mysql

volumes:
	inspection_mariadb_data:
		external: true
```

# Composeで起動
``` terminal
docker compose up -d
docker compose ps
docker compose logs mariadb
```

# 確認
``` terminal
docker compose exec mariadb mariadb -u root -p
show databases;
```
