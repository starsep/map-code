run: data/mazowieckie.gol
	python main.py

data/mazowieckie.gol:
	wget https://f003.backblazeb2.com/file/geodesk/mazowieckie.gol -O data/mazowieckie.gol

update:
	rm data/mazowieckie.gol
	make run