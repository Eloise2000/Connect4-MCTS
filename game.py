import pygame
import sys
from board import *
from connect4 import connect4
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

board = Board(1)

def main_screen():
    pygame.init()
    pygame.display.set_caption("Connect Four | AI Project")
    graphics_board = GBoard(board)

    start_button = graphics_board.create_button(60, 340, 300, 40, 'START', simulation)
    quit_button = graphics_board.create_button(60, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [start_button, quit_button]

    while True:
        graphics_board.write_on_board("CONNECT 4 GAME", graphics_board.PINK , 350 , 100, 60, True)
        graphics_board.write_on_board("CHOOSE START OR QUIT", graphics_board.GREEN , 350 , 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            button['callback']()
                
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.PINK
                    else:
                        button['color'] = graphics_board.WHITE

        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

def main(start = False):
    if not start:
        main_screen()
    print("\n")
    connect4()
    
def simulation():
    main(start = True)

if __name__ == '__main__':
    main()
    # If you want to just run with CLI, then run `connect4()` directly
    # connect4()