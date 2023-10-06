run: code/data/mazowieckie.gol
	cd code && ./gradlew run

code/data/mazowieckie.gol:
	wget https://f003.backblazeb2.com/file/geodesk/mazowieckie.gol -O code/data/mazowieckie.gol
