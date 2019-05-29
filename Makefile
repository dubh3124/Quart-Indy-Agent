buildup:
	docker-compose build && docker-compose up -d

buildIndyPool:
	docker build --build-arg pool_ip=192.168.50.45 -f /home/dubh3124/workspace/indy-sdk/ci/indy-pool.dockerfile -t indy_pool .

runIndyPool:
	docker run -itd -p 192.168.50.45:9701-9708:9701-9708 --name indy_pool indy_pool