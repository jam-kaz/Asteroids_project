"""Точка входа для запуска двумерной аркадной игры «Астероиды»."""

from src.game import AsteroidsGame
import pygame


def main() -> None:
    """Создает экземпляр игры и запускает главный цикл."""
    game = AsteroidsGame()
    game.run()


if __name__ == "__main__":
    main()
