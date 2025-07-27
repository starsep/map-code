run: data/mazowieckie.gol
	python main.py

data/mazowieckie.gol:
	curl https://osm.starsep.top/mazowieckie.gol -o data/mazowieckie.gol

update:
	rm data/mazowieckie.gol
	make run