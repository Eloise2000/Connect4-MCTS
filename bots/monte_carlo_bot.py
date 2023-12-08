import numpy as np
import random
import collections

class MonteCarloBot():
    def __init__(self, piece, show_steps = False, threshold=1e-2, window_size=50):
        self.piece = piece
        self.currentNode = None
        self.show_steps = show_steps # Whether print out the training steps
        self.threshold = threshold
        self.window_size = window_size

    def montecarlo_tree_search(self, board, currentNode):
        rootnode = Node(board=board)

        if currentNode is not None:
            rootnode = currentNode

        KPI_list = []
        epochs = 0
        # for i in range(1000): # Run 1000 times
        while not self.is_stable(KPI_list): # Check whether converges
            epochs += 1
            node = rootnode
            state = board.copy_board()
            if self.show_steps:
                print("*********** ROUND ", epochs, "***********")
                print("Actions explored (action, [win, visits]) :", rootnode.action_reward.items())
                print("UCT action last time:", rootnode.action)
                print("Not explored actions: ", node.available_actions)
                print("Total visits in root:", rootnode.total_visits)

            ''' selection '''
            # Keep going down the tree based on best UCT values until terminal or unexpanded node
            while node.available_actions == [] and node.children != []:
                # Drop the player
                node.selection()
                state.drop_piece(node.action, state.CURR_PLAYER)

                if self.show_steps:
                    print("print state in selection phase:")
                    state.print_board()

                # Drop the opponent
                col = random.choice(state.get_valid_locations())
                state.drop_piece(col, state.CURR_PLAYER)
                # Update the node after opponent drop
                node = node.proceed(state)

                if self.show_steps:
                    print("print state in selection phase:")
                    state.print_board()

                # Check whether the opponent win
                if state.winning_move(state.PREV_PLAYER):
                    break

            ''' expansion '''
            # If the game did not terminate, expands one random action and adds the node that one reaches
            if node.available_actions != [] and not state.winning_move(state.PREV_PLAYER):
                # Random drop the player
                col_player = random.choice(node.available_actions)
                state.drop_piece(col_player, state.CURR_PLAYER)

                if self.show_steps:
                    print("print state in expansion phase:")
                    state.print_board()

                # Random drop the opponent
                col_opponent = random.choice(state.get_valid_locations())
                state.drop_piece(col_opponent, state.CURR_PLAYER)
                # Update the node after opponent drop (expansion)
                node = node.expand(col_player, state)

                if self.show_steps:
                    print("print state in expansion phase:")
                    state.print_board()
            
            ''' simulation '''
            # If the game did not terminate, Random simulate both player and opponent
            while state.get_valid_locations():
                if state.winning_move(state.PREV_PLAYER):
                    break
                col = random.choice(state.get_valid_locations())
                state.drop_piece(col, state.CURR_PLAYER)

                if self.show_steps:
                    print("print state in simulation phase:")
                    state.print_board()

            ''' backtrack '''
            result = state.search_result(self.piece)
            while node is not None:
                node.update(result)
                node = node.parent

            if self.show_steps:
                print("Result is: ", result)

            KPI = rootnode.getKPI()
            KPI_list.append(KPI)

            if self.show_steps:
                print("KPI is:", KPI)
        
        best_action = rootnode.getAction()
        return best_action

    def is_stable(self, values):
        if len(values) < self.window_size:
            return False
        
        check_KPI = values[len(values) - self.window_size:len(values)]
        return max(abs(np.diff(check_KPI))) < self.threshold

    def get_move(self, board):
        if self.currentNode is None:
            self.currentNode = Node(board=board)
        
        if board.PREV_MOVE is not None:
            self.currentNode = self.currentNode.proceed(board)

        action_col = self.montecarlo_tree_search(board, self.currentNode)
        return action_col

class Node:
    def __init__(self, board, parent=None, action=None):
        self.board = board.copy_board()
        self.parent = parent
        self.available_actions = board.get_valid_locations()
        self.action_reward = collections.defaultdict(list) # key:available_actions; val:[wins, visits]
        self.action = action # which action was taken from here
        self.children = []
        self.total_wins = 0
        self.total_visits = 0

    def selection(self):
        # return child with largest UCT value
        # UCT = action.wins / action.visits + np.sqrt(2 * np.log(self.visits) / action.visits)
        uct_val = lambda x: x[1][0] / x[1][1] + np.sqrt(2 * np.log(self.total_visits) / x[1][1])
        action = sorted(self.action_reward.items(), key = uct_val)[-1][0] # best col action
        self.action = action
        return
    
    def proceed(self, board):
        for child in self.children:
            if child.board == board:
                return child
        child = Node(board = board, parent = self, action = self.action)
        self.children.append(child)
        return child
    
    def expand(self, action, board):
        # return child when move is taken
        # remove move from current node
        self.action = action
        child = Node(board = board, parent = self)
        self.available_actions.remove(action)
        self.children.append(child)
        return child

    def update(self, result):
        # The leaf expansion node don't record action
        if self.action != None:
            # First update total count
            self.total_wins += result
            self.total_visits += 1
            # Then update for the specific action
            if not self.action_reward[self.action]:
                self.action_reward[self.action] = [result, 1] # win, visits
            else:
                self.action_reward[self.action][0] += result # win
                self.action_reward[self.action][1] += 1 # visits

    def getKPI(self):
        return self.total_wins/self.total_visits
    
    def getAction(self):
        KPI = lambda x: x[1][0] / x[1][1]
        action = sorted(self.action_reward.items(), key = KPI)[-1][0] # best col action
        return action