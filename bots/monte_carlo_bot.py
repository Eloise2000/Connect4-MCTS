import numpy as np
import random
import collections

class MonteCarloBot():
    def __init__(self, piece, show_steps = False, threshold=0.05, window_size=50):
        self.piece = piece
        self.currentNode = None
        self.show_steps = show_steps # Whether print out the training steps
        self.threshold = threshold
        self.window_size = window_size

    def montecarlo_tree_search(self, board, currentNode):
        rootnode = Node(board=board)

        if currentNode is not None:
            rootnode = currentNode

        q_value_list = []
        epochs = 0

        ''' For convergence and UCT value check'''
        # action_last_time = []
        # q_value_0 = []
        # q_value_6 = []
        # is_stable_list = []

        # for i in range(500): # Run 500 times
        while not self.is_stable(q_value_list): # Check whether converges
            epochs += 1
            node = rootnode
            state = board.copy_board()
            
            ''' For convergence and UCT value check'''
            # is_stable_list.append(self.is_stable(q_value_list))
            # action_last_time.append(rootnode.action)
            # if 0 not in rootnode.action_reward:
            #     q_value_0.append(float("-inf"))
            # else:
            #     q_value_0.append(rootnode.action_reward[0][0]/rootnode.action_reward[0][1])
            # if 6 not in rootnode.action_reward:
            #     q_value_6.append(float("-inf"))
            # else:
            #     q_value_6.append(rootnode.action_reward[6][0]/rootnode.action_reward[6][1])
            

            if self.show_steps:
                print("*********** ROUND ", epochs, "***********")
                print("Actions explored (action, [reward, visits]) :", rootnode.action_reward.items())
                print("Best action based on UCT value last time:", rootnode.action)
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

            q_value = rootnode.get_q_value()
            q_value_list.append(q_value)

            if self.show_steps:
                print("Q value is:", q_value)
                
        ''' For convergence and UCT value check'''
        # print("action_last_time: ", action_last_time)
        # print("q_value_0",q_value_0)
        # print("q_value_6", q_value_6)
        # print("is_stable_list", is_stable_list)
        # print("q_value_list", q_value_list)
        
        print("Trained %d epochs" %epochs)
        print("Action, reward, visits are: ", rootnode.action_reward.items())
        best_action = rootnode.getAction()
        return best_action
    
    def is_stable(self, values):
        if len(values) < self.window_size:
            return False
        
        check_q_value = values[len(values) - self.window_size:len(values)]
        return (max(check_q_value) - min(check_q_value)) < self.threshold

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
        self.action_reward = collections.defaultdict(list) # key:available_actions; val:[rewards, visits]
        self.action = action # which action was taken from here
        self.children = []
        self.total_rewards = 0
        self.total_visits = 0

    def selection(self):
        # return child with largest UCT value
        # UCT = action.rewards / action.visits + np.sqrt(2 * np.log(self.visits) / action.visits)
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
            self.total_rewards += result
            self.total_visits += 1
            # Then update for the specific action
            if not self.action_reward[self.action]:
                self.action_reward[self.action] = [result, 1] # reward, visits
            else:
                self.action_reward[self.action][0] += result # reward
                self.action_reward[self.action][1] += 1 # visits

    def get_q_value(self):
        return self.total_rewards/self.total_visits
    
    def getAction(self):
        q_value = lambda x: x[1][0] / x[1][1]
        action = sorted(self.action_reward.items(), key = q_value)[-1][0] # best col action
        return action