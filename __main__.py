import sys
from game import Game

def main(args=None):
    if args is None:
        args = sys.argv[:1]
    game = Game()
    print("Initializing game...")
    game.run()

if __name__ == '__main__':
    sys.exit(main())