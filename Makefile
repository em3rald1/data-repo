build:
	py urcl-to-bin.py bash.urcl game.bin
run:
	uemu -r game.bin
vmbuild:
	g++ urcl-emu.cpp -o uemu
debug:
	uemu -d game.bin