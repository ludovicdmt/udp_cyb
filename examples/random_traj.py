#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This example sends random left/right and forward command, drawn for uniform distribution.
With the wheelchair mini-game, it would make some incremental movements.

Author: Ludovic Darmet
email: ludovic.darmet@gmail.com
"""
__author__ = "Ludovic Darmet"

import numpy as np
import time

from udp_cyb import UDPClient

def ema(prices: list, period: int) -> float:
    """Calculate exponential moving average.

    Args:
        prices (list): List of prices.
        period (int): Number of periods.
    Returns:
        float: Exponential moving average.
    """
    if len(prices) < period:  # Can't calculate EMA at the start
        return np.mean(prices)
    else:
        return ema_helper(prices, period, (2 / (period + 1)), len(prices))


def ema_helper(prices: list, N: int, k: float, length: int) -> float:
    """Recursive function to calculate EMA.

    Args:
        prices (list): List of prices.
        N (int): Number of periods.
        k (float): Smoothing factor.
        length (int): Length of the list of prices.
    Returns:
        float: Exponential moving average.
    """
    if len(prices) == length - N:
        return prices[0]
    res_ema = prices[N - 1]
    for t in range(N, length):
        res_ema = prices[t] * k + res_ema * (1 - k)
    return res_ema

# Run on localhost and default port.
client = UDPClient(ip = "localhost", port = 59075)
client.start()
tic = time.perf_counter()
pred_history = [0.5]

x = [0]
theta = [0]


while len(x)<300:
    last_x = x[-1]
    last_theta = theta[-1]
    # Start only when control and device is sent by the game
    if client.control == True:
        if client.device == "arm":
            forward = 0.6
            tresh_tongue = 0.522
            tresh_M1 = 0.505
            tresh_M2 = 0.51
        else:
            forward = 0.5
            tresh_tongue = 0.52
            tresh_M1 = 0.51
            tresh_M2 = 0.51 # Bias to right
        pred_M1 = np.random.uniform(0.47, 0.53)
        pred_lr = np.random.uniform(0.3, 0.6)
        pred = [pred_lr, 1-pred_lr]
        pred_tongue = np.random.uniform(0.48, 0.55)
        # Make sure the value is between -1 and 1
        if pred_tongue > tresh_tongue:
            if pred_M1 > tresh_M1:
                pred_class = np.argmax(pred)
                pred_proba = np.max(pred)
                pred_history.append(pred_proba if pred_class == 1 else 1 - pred_proba)
            else:
                client.send_command(0, 0, 0, forward)
                x.append(last_x+forward)
                theta.append(last_theta)
                continue

        # Handle left vs right MI
        elif pred_M1 > tresh_M1:
            pred_class = np.argmax(pred)
            pred_proba = np.max(pred)
            pred_history.append(pred_proba if pred_class == 1 else 1 - pred_proba)
        else:
            continue
        # Update prediction history and calculate EMA
        pred_history.pop(0)
        ema_pred = ema(pred_history, 1)

        # Make a prediction based on the EMA
        print(f"Ema pred: {ema_pred}, proba: {pred_proba}")
        if ema_pred > tresh_M2:
            client.send_command(0, 0, +0.2, 0) # Rotate right
            x.append(last_x)
            theta.append(last_theta+0.2)
        elif ema_pred < tresh_M2:
            client.send_command(0, 0, -0.2, 0) # Rotate left
            x.append(last_x)
            theta.append(last_theta-0.2)

        tac = time.perf_counter()
        while tac - tic < 0.25:
            tac = time.perf_counter()
        tic = time.perf_counter()

        # Save the array to a file
        data = np.array([x, theta]).T  
        np.save('trajectory_data.npy', data) 
