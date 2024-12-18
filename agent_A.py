# -*- coding: utf-8 -*-
from collections import deque
import heapq

def manhattan_distance(arr1, arr2):
    return abs(arr1[0] - arr2[0]) + abs(arr1[1] - arr2[1])

def locate_destination(game_map):
    for x in range(len(game_map)):
        for y in range(len(game_map[0])):
            if game_map[x][y] == 'goal':
                return (x, y)
    return None

def evaluate_coin_attraction(position, coins, cost_multiplier):
    if not coins:
        return 0
    coin_attraction = 0
    for coin_pos in coins:
        dist_to_coin = manhattan_distance(position, coin_pos)
        net_value = 20 - (dist_to_coin * cost_multiplier)
        if net_value > 0:
            coin_attraction += net_value / (dist_to_coin + 1)

    return coin_attraction

def assess_car_risk(position, vehicle_positions):
    if not vehicle_positions:
        return 0
    risk = 0
    for vehicle_pos in vehicle_positions:
        dist = manhattan_distance(position, vehicle_pos)
        if dist <= 2:
            risk += (3 - dist) * 5
    return risk

def determine_possible_movements(game_map, position, current_vehicle_positions):
    x, y = position
    moves = {
        'W': (x, y - 1),
        'D': (x + 1, y),
        'S': (x, y + 1),
        'A': (x - 1, y),
        'I': (x, y)
    }
    m, n = len(game_map), len(game_map[0])
    valid_moves = []
    for move, (new_x, new_y) in moves.items():
        if (new_x in range(m) and new_y in range(n) and game_map[new_x][new_y] != 'wall' and (new_x, new_y) not in current_vehicle_positions):
            valid_moves.append((move, (new_x, new_y)))
    return valid_moves

def compute_path_score(position, destination_pos, coins, vehicle_positions, path_cost, cost_multiplier):
    distance_penalty = manhattan_distance(position, destination_pos) * cost_multiplier
    coin_potential = evaluate_coin_attraction(position, coins, cost_multiplier)
    car_danger = assess_car_risk(position, vehicle_positions)
    return distance_penalty - coin_potential + car_danger + path_cost

def select_nearest_coin(current_position, coins):
    if not coins:
        return None
    return min(coins, key=lambda coin: manhattan_distance(current_position, coin))

def a_star(game_map, start_pos, destination_pos, available_coins, vehicle_positions, cost_multiplier):
    open_set = [(compute_path_score(start_pos, destination_pos, available_coins, vehicle_positions, 0, cost_multiplier),
                 0, start_pos, [])]
    heapq.heapify(open_set)
    path_costs = {start_pos: 0}
    explored_positions = set()
    while open_set:
        f_score, path_cost, current_pos, path = heapq.heappop(open_set)
        if current_pos == destination_pos:
            return path[0] if path else 'I'

        if current_pos in explored_positions:
            continue

        explored_positions.add(current_pos)

        possible_moves = determine_possible_movements(game_map, current_pos, vehicle_positions)

        for move, next_pos in possible_moves:
            if next_pos in explored_positions:
                continue

            tentative_cost = path_cost + cost_multiplier

            if next_pos not in path_costs or tentative_cost < path_costs[next_pos]:
                path_costs[next_pos] = tentative_cost
                h_score = compute_path_score(next_pos, destination_pos, available_coins,
                                               vehicle_positions, tentative_cost, cost_multiplier)
                new_path = path + [move]
                heapq.heappush(open_set, (h_score, tentative_cost, next_pos, new_path))

    return 'I'

def no_coins_in_5x5_area(position, coins):
    x, y = position
    for coin_x, coin_y in coins:
        if abs(coin_x - x) <= 2 and abs(coin_y - y) <= 2:
            return False
    return True

def strategy_decision(game_map, current_position, available_coins, vehicle_positions, cost_multiplier):
    if not hasattr(strategy_decision, "state"):
        strategy_decision.state = 'collecting_coins'

    destination_pos = locate_destination(game_map)
    if not destination_pos:
        return 'I'

    if current_position == destination_pos:
        return 'I'

    if strategy_decision.state == 'collecting_coins' and no_coins_in_5x5_area(current_position, available_coins):
        strategy_decision.state = 'going_to_goal'

    if strategy_decision.state == 'collecting_coins' and available_coins:
        nearest_coin = select_nearest_coin(current_position, available_coins)
        if nearest_coin:
            return a_star(game_map, current_position, nearest_coin,
                                            available_coins, vehicle_positions, cost_multiplier)

    return a_star(game_map, current_position, destination_pos, available_coins, vehicle_positions, cost_multiplier)

def logic_A(cur_map, cur_position, cur_coins, cur_car_positions, penalty_k):
    return strategy_decision(cur_map, cur_position, cur_coins, cur_car_positions, penalty_k)
