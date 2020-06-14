from __future__ import print_function

__author__ = "Ben Reuveni - ben.reuveni@gmail.com"
__date__ = "1.3.18"

import numpy as np, math, random, operator, sys, os
from psychopy import visual, core, event, logging, gui
from scipy.optimize import minimize
from scipy.stats import norm
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import matplotlib.patches as pch
from matplotlib import cm
from multiprocessing import Process, Manager, Queue, Pool
import time, warnings

count = 0

p_a_matrix_a = np.loadtxt('p_a_matrix_a.txt')
matrix_dist_max_size = float(1)
matrix_pn_max_size = float(7)
matrix_dist_step_size = matrix_dist_max_size / float(100)
matrix_pn_step_size = matrix_pn_max_size / float(100)
default_dm_noise_sd = None
default_pn_noise_sd = None
pa_transform = 1  # turning this on returns p(A) values from 0 - 1. With it off it returns p(A) from 0.5-1 due to how we calculate.

# trial evaluation starts from trial 2. Trial 1 is used to initialize the db
# max trials = 639 (base 0)
plot_start = 0
trial_start = 1
# trial_num = 640
debug = 0
plotting = 0
logging = 0

'''
PINNACLE is called 'p' (incase we wanted more than 1 instance)

For memory modules:
p.ii = ii
mm2 = rb_x
mm3 = rb_y
'''

class pinnacle:
    def __init__(self, dm_noise, pn_noise):
        self.dm_noise_sd = dm_noise
        self.pn_noise_sd = pn_noise

        self.ii = None
        self.rbx = None
        self.rby = None

        self.rb_winner = None
        self.rb_winner_pA = None
        self.rb_winner_a_or_b = None
        self.rb_dist = None

        self.pA_given_ii = None
        self.pR = None
        self.log_pR = 0
        self.dom = None

    def calc_pA(self, x, y):
        if debug == 2: '\n### in pA calc ###'

        # ii
        b = self.ii.db
        E_x = y - b
        ii_left_or_right = (x - E_x)
        dist_to_E = (abs(ii_left_or_right))
        ii_dist_to_db = (dist_to_E * 0.7071067811865475)

        if ii_dist_to_db > 0.98:
            ii_dist_to_db = 0.98

        ii_dist_lower = (int(ii_dist_to_db / matrix_dist_step_size) * matrix_dist_step_size)
        ii_dist_upper = (round(ii_dist_lower + matrix_dist_step_size, 2))

        if self.ii.ps > 6.86:
            self.ii.ps = 6.86

        if self.ii.ps < self.pn_noise_sd:
            self.ii.ps = self.pn_noise_sd

        ii_ps_lower = int(self.ii.ps / matrix_pn_step_size) * matrix_pn_step_size
        ii_ps_upper = ii_ps_lower + matrix_pn_step_size

        ii_denom = (round((ii_ps_upper - ii_ps_lower) * (ii_dist_upper - ii_dist_lower), 4))

        i_ps_lower_ii = (int((self.ii.ps / matrix_pn_max_size) * 100) + 1)
        i_ps_upper_ii = (i_ps_lower_ii + 1)

        i_dist_lower_ii = (int((ii_dist_to_db / matrix_dist_max_size) * 100) + 1)
        i_dist_upper_ii = (i_dist_lower_ii + 1)

        # interpolate p(A)
        ii_pA = (
            ((((ii_ps_upper - self.ii.ps) * (ii_dist_upper - ii_dist_to_db)) / ii_denom) * p_a_matrix_a[
                i_dist_lower_ii - 1, i_ps_lower_ii - 1])
            + ((((ii_dist_to_db - ii_dist_lower) * (ii_ps_upper - self.ii.ps)) / ii_denom) * p_a_matrix_a[
                i_dist_upper_ii - 1, i_ps_lower_ii - 1])
            + ((((ii_dist_upper - ii_dist_to_db) * (self.ii.ps - ii_ps_lower)) / ii_denom) * p_a_matrix_a[
                i_dist_lower_ii - 1, i_ps_upper_ii - 1])
            + ((((ii_dist_to_db - ii_dist_lower) * (self.ii.ps - ii_ps_lower)) / ii_denom) * p_a_matrix_a[
                i_dist_upper_ii - 1, i_ps_upper_ii - 1]))

        if ii_pA > 0.99999:
            ii_pA = 0.9999
        elif ii_pA < 0:
            ii_pA = 0.0001

        # default to "A" but flip it if needed in the next bit
        self.ii.a_or_b = 1
        if ii_left_or_right > 0:  # it's a B
            if pa_transform == 1:
                ii_pA = (1 - ii_pA)
            self.ii.a_or_b = 2

        self.ii.pA = ii_pA
        self.ii.dist = ii_dist_to_db
        if debug == 2: print('ii db is:  ' + str(self.ii.db) + ' ii ps is:  ' + str(self.ii.ps) + ' ii pA is:  ' + str(
            self.ii.pA) + ' and voted for ' + str(self.ii.a_or_b) + ' dist is: ' + str(self.ii.dist))

        # rbx
        x1 = self.rbx.db
        y1 = 20

        x2 = self.rbx.db
        y2 = 80

        rbx_dist_to_db = (abs(((y2 - y1) * x) - ((x2 - x1) * y) + (x2 * y1) - (y2 * x1))
                          / math.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2)))

        rbx_left_or_right = ((x - x1) * (y2 - y1) - (y - y1) * (x2 - x1))

        if rbx_dist_to_db > 0.98:
            rbx_dist_to_db = 0.98

        rbx_dist_lower = (int(rbx_dist_to_db / matrix_dist_step_size) * matrix_dist_step_size)
        rbx_dist_upper = (round(rbx_dist_lower + matrix_dist_step_size, 2))

        if self.rbx.ps > 6.86:
            self.rbx.ps = 6.86

        if self.rbx.ps < self.pn_noise_sd:
            self.rbx.ps = self.pn_noise_sd

        rbx_ps_lower = int(self.rbx.ps / matrix_pn_step_size) * matrix_pn_step_size
        rbx_ps_upper = rbx_ps_lower + matrix_pn_step_size

        rbx_denom = (round((rbx_ps_upper - rbx_ps_lower) * (rbx_dist_upper - rbx_dist_lower), 4))

        i_ps_lower_rbx = (int((self.rbx.ps / matrix_pn_max_size) * 100) + 1)
        i_ps_upper_rbx = (i_ps_lower_rbx + 1)

        i_dist_lower_rbx = (int((rbx_dist_to_db / matrix_dist_max_size) * 100) + 1)
        i_dist_upper_rbx = (i_dist_lower_rbx + 1)

        # interpolate p(A)
        rbx_pA = (
            ((((rbx_ps_upper - self.rbx.ps) * (rbx_dist_upper - rbx_dist_to_db)) / rbx_denom) * p_a_matrix_a[
                i_dist_lower_rbx - 1, i_ps_lower_rbx - 1])
            + ((((rbx_dist_to_db - rbx_dist_lower) * (rbx_ps_upper - self.rbx.ps)) / rbx_denom) * p_a_matrix_a[
                i_dist_upper_rbx - 1, i_ps_lower_rbx - 1])
            + ((((rbx_dist_upper - rbx_dist_to_db) * (self.rbx.ps - rbx_ps_lower)) / rbx_denom) * p_a_matrix_a[
                i_dist_lower_rbx - 1, i_ps_upper_rbx - 1])
            + ((((rbx_dist_to_db - rbx_dist_lower) * (self.rbx.ps - rbx_ps_lower)) / rbx_denom) * p_a_matrix_a[
                i_dist_upper_rbx - 1, i_ps_upper_rbx - 1]))

        if rbx_pA > 0.99999:
            rbx_pA = 0.9999
        elif rbx_pA < 0:
            rbx_pA = 0.0001

        # default to "A" but flip it if needed in the next bit
        self.rbx.a_or_b = 1
        if rbx_left_or_right > 0:  # it's a B
            if pa_transform == 1:
                rbx_pA = (1 - rbx_pA)
            self.rbx.a_or_b = 2

        self.rbx.pA = rbx_pA
        self.rbx.dist = rbx_dist_to_db
        if debug == 2: print(
            'rbx db is: ' + str(self.rbx.db) + ' rbx ps is: ' + str(self.rbx.ps) + ' rbx pA is: ' + str(
                self.rbx.pA) + ' and voted for ' + str(self.rbx.a_or_b) + ' dist is: ' + str(self.rbx.dist))

        # rby
        x1 = 20
        y1 = self.rby.db

        x2 = 80
        y2 = self.rby.db

        rby_dist_to_db = (abs(((y2 - y1) * x) - ((x2 - x1) * y) + (x2 * y1) - (y2 * x1))
                          / math.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2)))

        rby_left_or_right = ((x - x1) * (y2 - y1) - (y - y1) * (x2 - x1))

        if rby_dist_to_db > 0.98:
            rby_dist_to_db = 0.98

        rby_dist_lower = (int(rby_dist_to_db / matrix_dist_step_size) * matrix_dist_step_size)
        rby_dist_upper = (round(rby_dist_lower + matrix_dist_step_size, 2))

        if self.rby.ps > 6.86:
            self.rby.ps = 6.86

        if self.rby.ps < self.pn_noise_sd:
            self.rby.ps = self.pn_noise_sd

        rby_ps_lower = int(self.rby.ps / matrix_pn_step_size) * matrix_pn_step_size
        rby_ps_upper = rby_ps_lower + matrix_pn_step_size

        rby_denom = (round((rby_ps_upper - rby_ps_lower) * (rby_dist_upper - rby_dist_lower), 4))

        i_ps_lower_rby = (int((self.rby.ps / matrix_pn_max_size) * 100) + 1)
        i_ps_upper_rby = (i_ps_lower_rby + 1)

        i_dist_lower_rby = (int((rby_dist_to_db / matrix_dist_max_size) * 100) + 1)
        i_dist_upper_rby = (i_dist_lower_rby + 1)

        # interpolate p(A)
        rby_pA = (
            ((((rby_ps_upper - self.rby.ps) * (rby_dist_upper - rby_dist_to_db)) / rby_denom) * p_a_matrix_a[
                i_dist_lower_rby - 1, i_ps_lower_rby - 1])
            + ((((rby_dist_to_db - rby_dist_lower) * (rby_ps_upper - self.rby.ps)) / rby_denom) * p_a_matrix_a[
                i_dist_upper_rby - 1, i_ps_lower_rby - 1])
            + ((((rby_dist_upper - rby_dist_to_db) * (self.rby.ps - rby_ps_lower)) / rby_denom) * p_a_matrix_a[
                i_dist_lower_rby - 1, i_ps_upper_rby - 1])
            + ((((rby_dist_to_db - rby_dist_lower) * (self.rby.ps - rby_ps_lower)) / rby_denom) * p_a_matrix_a[
                i_dist_upper_rby - 1, i_ps_upper_rby - 1]))

        if rby_pA > 0.99999:
            rby_pA = 0.9999
        elif rby_pA < 0:
            rby_pA = 0.0001

        # default to "A" but flip it if needed in the next bit
        self.rby.a_or_b = 1
        if rby_left_or_right > 0:  # it's a B
            if pa_transform == 1:
                rby_pA = (1 - rby_pA)
            self.rby.a_or_b = 2

        self.rby.pA = rby_pA
        self.rby.dist = rby_dist_to_db
        if debug == 2: print(
            'rby db is: ' + str(self.rby.db) + ' rby ps is: ' + str(self.rby.ps) + ' rby pA is: ' + str(
                self.rby.pA) + ' and voted for ' + str(self.rby.a_or_b) + ' dist is: ' + str(self.rby.dist))

    def calc_pR(self, subj_resp):  # , dm_noise_disro):
        global pA_given_ii_array
        if debug == 2:
            print('rb winner is: ' + str(self.rb_winner))
            print('\n### in pR calc ###')


        self.pA_given_ii = (1.0 + math.erf((abs(0.5 - self.ii.pA) - abs(0.5 - self.rb_winner_pA))
                                           / math.sqrt(2.0))) / 2.0

        pA_given_rb = 1 - self.pA_given_ii

        # pA_given_ii_array.append(self.pA_given_ii)
        pA_temp = (self.pA_given_ii * self.ii.pA) + (pA_given_rb * self.rb_winner_pA)


        if subj_resp == 1:
            self.pR = pA_temp
            self.log_pR += math.log10(pA_temp)
        else:
            self.pR = 1 - pA_temp
            self.log_pR += math.log10((1 - pA_temp))

        if debug == 2: print('pR is: ' + str(self.pR))

    def feedback(self, subj_resp, label):

        if debug == 2: print('\n### in Feedback ###')

        if self.ii.a_or_b == self.rb_winner_a_or_b != subj_resp:

            if debug == 2:
                print('no system voted like the subject. calculating which to flip')
                print(self.ii.dist, self.rbx.dist, self.rby.dist)

            # who was closer?
            # dist_array = [self.ii.dist, self.rb_dist]
            # closest_dist = dist_array.index(min(dist_array))

            if self.ii.dist < self.rb_dist:  # ii was closer to the line
                self.ii.pA = 0.5
                self.ii.a_or_b = subj_resp
                self.ii.feedback = 1
                self.dom = 1
                if debug == 2: print('ii flipped with a dist of: ' + str(self.ii.dist))

                self.rbx.feedback = 0
                if self.rbx.a_or_b == label:
                    self.rbx.feedback = 1
                    if debug == 2: print('rbx agreed with the label')

                self.rby.feedback = 0
                if self.rby.a_or_b == label:
                    self.rby.feedback = 1
                    if debug == 2: print('rby agreed with the label')

            else:  # rb was closer to the bound
                self.rb_winner_pA = 0.5
                self.rb_winner_a_or_b = subj_resp

                if self.rb_winner == 2:
                    self.rbx.pA = 0.5
                    self.rbx.a_or_b = subj_resp
                    self.rbx.feedback = 1
                    self.dom = 2
                    if debug == 2: print('rbx was flipped with a dist of: ' + str(1 - self.rb_dist))

                    self.rby.feedback = 0
                    if self.rby.a_or_b == label:
                        self.rby.feedback = 1
                        if debug == 2: print('rby agreed with the label')

                if self.rb_winner == 3:
                    self.rby.pA = 0.5
                    self.rby.a_or_b = subj_resp
                    self.rby.feedback = 1
                    self.dom = 3
                    if debug == 2: print('rby was flipped with a dist of: ' + str(self.rb_dist))

                    self.rbx.feedback = 0
                    if self.rbx.a_or_b == label:
                        self.rbx.feedback = 1
                        if debug == 2: print('rbx agreed with label')

                self.ii.feedback = 0
                if self.ii.a_or_b == label:
                    self.ii.feedback = 1
                    if debug == 2: print('ii agreed with label')

        elif (
                self.ii.a_or_b == subj_resp and self.rb_winner_a_or_b != subj_resp):  # one of the dbms voted like the subj

            '''
            if at least 1 system voted like the subj, they drove behavior.
            '''
            self.ii.feedback = 1
            self.dom = 1
            if debug == 2:
                print('only II voted like subj.')

            self.rbx.feedback = 0
            if self.rbx.a_or_b == label:
                self.rbx.feedback = 1
                if debug == 2: print('rbx agreed with label')

            self.rby.feedback = 0
            if self.rby.a_or_b == label:
                self.rby.feedback = 1
                if debug == 2:
                    print('rby feedback is: ' + str(self.rby.feedback))
                    print('rby agreed with label')

        elif self.ii.a_or_b != subj_resp and self.rb_winner_a_or_b == subj_resp:  # rb is dom
            if debug == 2:
                print('only RB voted like the subj')

            if self.rb_winner == 2:
                self.rbx.feedback = 1
                self.dom = 2
                if debug == 2: print('rbx is dom with a pA of: ' + str(1 - self.pA_given_ii))

                self.rby.feedback = 0
                if self.rby.a_or_b == label:
                    self.rby.feedback = 1
                    if debug == 2: print('rby agreed with label')

            elif self.rb_winner == 3:
                self.rby.feedback = 1
                self.dom = 3
                if debug == 2: print('rby is dom with a pA of: ' + str(1 - self.pA_given_ii))

                self.rbx.feedback = 0
                if self.rbx.a_or_b == label:
                    self.rbx.feedback = 1
                    if debug == 2: print('rbx agreed with label')

            self.ii.feedback = 0
            if self.ii.a_or_b == label:
                self.ii.feedback = 1
                if debug == 2: print('ii agreed with label')

        elif self.ii.a_or_b == self.rb_winner_a_or_b == subj_resp:
            if debug == 2: print('both systems voted like the subj')
            '''
            if both systems voted like the subj, base it on dom system
            '''
            if self.pA_given_ii >= 0.5:
                self.dom = 1
                self.ii.feedback = 1
                if debug == 2: print('ii is dom and voted')

                self.rbx.feedback = 0
                if self.rbx.a_or_b == label:
                    self.rbx.feedback = 1
                    if debug == 2: print('rbx agreed with label')

                self.rby.feedback = 0
                if self.rby.a_or_b == label:
                    self.rby.feedback = 1
                    if debug == 2: print('rby agreed with label')

            else:

                if self.rb_winner == 2:
                    self.dom = 2
                    self.rbx.feedback = 1
                    if debug == 2: print('rbx is dom and voted')

                    self.rby.feedback = 0
                    if self.rby.a_or_b == label:
                        self.rby.feedback = 1
                        if debug == 2: print('rby agreed with label')

                elif self.rb_winner == 3:
                    self.dom = 3
                    self.rby.feedback = 1
                    if debug == 2: print('rby is dom and voted')

                    self.rbx.feedback = 0
                    if self.rbx.a_or_b == label:
                        self.rbx.feedback = 1
                        if debug == 2: print('rbx agreed with label')

                self.ii.feedback = 0
                if self.ii.a_or_b == label:
                    self.ii.feedback = 1
                    if debug == 2: print('ii agreed with label')

    def learn(self, label, x, y):
        if debug == 2:
            print('\n### in Learn ###')
            print(self.ii.feedback, self.rbx.feedback, self.rby.feedback)
        # ii
        self.ii.RPE = self.ii.pA
        if label == 1:
            self.ii.RPE = 1 - self.ii.pA
            if debug == 2: print('ii RPE is: ' + str(self.ii.RPE))

        if self.ii.feedback == 1:
            self.ii.ps = self.ii.ps * (1 - (self.ii.RPE * self.ii.ps_lr))
            if self.ii.ps < self.pn_noise_sd:
                self.ii.ps = self.pn_noise_sd
            if debug == 2:
                print('ii is correct')
                print('new ii ps is: ' + str(self.ii.ps))

        elif self.ii.feedback == 0:
            self.ii.ps = self.ii.ps / (1 - (self.ii.RPE * self.ii.ps_lr))
            if self.ii.a_or_b == 1:
                self.ii.db += self.ii.db_lr
            elif self.ii.a_or_b == 2:
                self.ii.db -= self.ii.db_lr
            if debug == 2:
                print(' ii is wrong')
                print('new ii ps is: ' + str(self.ii.ps))
                print('new ii db is: ' + str(self.ii.db))

        # rbx
        self.rbx.RPE = self.rbx.pA
        if label == 1:
            self.rbx.RPE = 1 - self.rbx.pA
            if debug == 2: print('rbx RPE is: ' + str(self.rbx.RPE))

        if self.rbx.feedback == 1:

            self.rbx.ps = self.rbx.ps * (1 - (self.rbx.RPE * self.rbx.ps_lr))
            if self.rbx.ps < self.pn_noise_sd:
                self.rbx.ps = self.pn_noise_sd
            if debug == 2:
                print('rbx is correct')
                print('new rbx ps is: ' + str(self.rbx.ps))

        elif self.rbx.feedback == 0:

            self.rbx.ps = self.rbx.ps / (1 - (self.rbx.RPE * self.rbx.ps_lr))
            self.rbx.db = x
            if debug == 2:
                print(' rbx is wrong')
                print('new rbx ps is: ' + str(self.rbx.ps))
                print('new rbx db is: ' + str(self.rbx.db))

        # rby
        self.rby.RPE = self.rby.pA
        if label == 1:
            self.rby.RPE = 1 - self.rby.pA
        if debug == 2: print('rby RPE is: ' + str(self.rby.RPE))

        if self.rby.feedback == 1:

            self.rby.ps = self.rby.ps * (1 - (self.rby.RPE * self.rby.ps_lr))
            if self.rby.ps < self.pn_noise_sd:
                self.rby.ps = self.pn_noise_sd
            if debug == 2:
                print('rby is correct')
                print('new rby ps is: ' + str(self.rby.ps))


        elif self.rby.feedback == 0:
            self.rby.ps = self.rby.ps / (1 - (self.rby.RPE * self.rby.ps_lr))
            self.rby.db = y
            if debug == 2:
                print(' rby is wrong')
                print('new rby ps is: ' + str(self.rby.ps))
                print('new rbx db is: ' + str(self.rby.db))

class dbm:
    def __init__(self, slope, ps, rb_ps_lr, ii_ps_lr, ii_db_lr):

        self.db = None
        self.pA = None
        self.a_or_b = None
        self.dist = None
        self.feedback = None
        self.RPE = None
        self.flipped = 0

        if slope == 1:  # ii
            self.db_lr = ii_db_lr
            self.ps = ps
            self.ps_lr = ii_ps_lr

        else:
            self.db_lr = 'Jumps'
            self.ps = ps
            self.ps_lr = rb_ps_lr

def normalize_space(data):
    x_array = data[:, 0]
    y_array = data[:, 1]

    norm_x_array = []
    norm_y_array = []

    min_x = min(x_array)
    min_y = min(y_array)

    max_x = max(x_array)
    max_y = max(y_array)

    for x in range(0, len(x_array)):
        norm_x_array.append((x_array[x] - min_x) / (max_x - min_x))
        norm_y_array.append((y_array[x] - min_y) / (max_y - min_y))

    data[:, 0] = norm_x_array
    data[:, 1] = norm_y_array

    return (data)

class TimeOut(Exception):
    # timeout class
    pass

def test(xk):
    # warnings.warn("killing")
    print(xk)

def do_bns(par, switches, data):  # , NLL, q):#, trial_num):
    # just some book-keeping
    global pR_array, ii_pA_array, rbx_pA_array, rby_pA_array, pA_given_ii_array, plotting, \
        rbx_db_array, rby_db_array, ii_db_array, ii_pS_array, rbx_pS_array, rby_pS_array, dom_sys, count

    count += 1
    trial_num = switches[0]
    optimizing = switches[1]
    evaluating = switches[2]
    logging = switches[3]
    subj_num = switches[4]
    trial_start_array = switches[5]
    block = switches[6]

    par = [abs(y) for y in par]  # ensure all values are positive if using unbounded optimization

    if logging == 1:
        #pinn_log = open('E:/Bait and Switch Tutor/pinn_files/subj_' + str(switches[4]) + '/subj_' + str(switches[4]) + '_pin_log_1-' + str(trial_num) + '.txt', 'w')
        pinn_log = open('./pinn_files/subj_' + str(subj_num) + '/subj_' + str(subj_num) + '_pin_log_1-' + str(trial_num) + '.txt', 'w')
        pinn_log.write('t, x, y, label, subj_resp, p.dom, p.rb_winner, '
                       'p.ii.ps, p.ii.db, p.ii.pA, p.ii.a_or_b, p.ii.feedback, p.ii.flipped, '
                       'p.rbx.ps, p.rbx.db, p.rbx.pA, p.rbx.a_or_b, p.rbx.feedback, p.rbx.flipped, '
                       'p.rby.ps, p.rby.db, p.rby.pA, p.rby.a_or_b, p.rby.feedback, p.rby.flipped, block_time, block\n')
        pinn_log.write('%f %f %f %f %f %f\n' % (par[0], par[1], par[2], par[3], par[4], par[5]))

    if debug == 1:
        print((str(count) + " par in do_bns is: " + str(par)))

    # initializes Pinnacle
    p = pinnacle(par[4], par[5])

    # initiate memory modules
    p.ii = dbm(1, par[0], par[1], par[2], par[3])
    p.rbx = dbm(2, par[0], par[1], par[2], par[3])
    p.rby = dbm(3, par[0], par[1], par[2], par[3])

    # initiate points
    p.ii.db = data[0][1] - data[0][0]  # ori - sf (assuming slope = 1)
    p.rbx.db = data[0][0]  # sf
    p.rby.db = data[0][1]  # ori


    for t in range(trial_start, len(data)):  # for each trial

        x = data[t][0]
        y = data[t][1]
        label = data[t][2]
        subj_resp = data[t][3]

        if debug == 2:
            print('\n-----Trial ' + str(t) + '-----')
            print(x, y, label, subj_resp)

        # calculate p(A) for each module
        pinnacle.calc_pA(p, x, y)

        # pick a winning RB module to compete with II - winner takes all
        # we use the index of the winner to retrieve appropriate values
        rb_xy_pA = [abs(0.5 - p.rbx.pA), abs(0.5 - p.rby.pA)]
        p.rb_winner = rb_xy_pA.index(max(rb_xy_pA)) + 2  # so that the index is either '2' or '3'

        p.rb_winner_pA = p.rbx.pA
        p.rb_winner_a_or_b = p.rbx.a_or_b
        p.rb_dist = p.rbx.dist
        if p.rb_winner == 3:
            p.rb_winner_pA = p.rby.pA
            p.rb_winner_a_or_b = p.rby.a_or_b
            p.rb_dist = p.rby.dist

        if debug == 2: print(p.rb_dist, p.rbx.dist, p.rby.dist)

        # pinnacle.calc_pR(p, subj_resp, dm_noise_distro.dm_dist)
        pinnacle.calc_pR(p, subj_resp)

        # get feedback for each module
        pinnacle.feedback(p, subj_resp, label)

        trial_start_time = trial_start_array[t]
        #print(trial_start_time)

        if logging == 1:
            pinn_log.write('%i %f %f %i %i %i %i %f %f %f %i %i %i %f %f %f %i %i %i %f %f %f %i %i %i %f %i\n' % (
                t, x, y, label, subj_resp, p.dom, p.rb_winner,
                p.ii.ps, p.ii.db, p.ii.pA, p.ii.a_or_b, p.ii.feedback, p.ii.flipped,
                p.rbx.ps, p.rbx.db, p.rbx.pA, p.rbx.a_or_b, p.rbx.feedback, p.rbx.flipped,
                p.rby.ps, p.rby.db, p.rby.pA, p.rby.a_or_b, p.rby.feedback, p.rby.flipped,
                trial_start_time, block))

        # learn
        pinnacle.learn(p, label, x, y)


    if debug == 1:
        print(p.log_pR * -1)

    if optimizing == 1:
        return p.log_pR * -1
    elif evaluating == 1:
        return [p.ii.ps, p.rbx.ps, p.rby.ps], [p.ii.db, p.rbx.db, p.rby.db]



# data = np.loadtxt('C:/Users/Ben/Google Drive/fMRI/data/Tutor Pilot - 1_22_18/pre fmri trial estimations/1_29_18/pinn files/subj 1.txt')
#
# stims = np.loadtxt('C:/Users/Ben/Google Drive/fMRI/data/Tutor Pilot - 1_22_18/pre fmri trial estimations/1_29_18/pinn files/subj 1 stims.txt')
#
# optimizing = 0
# evaluating = 1
# logging = 1
# trial_num = 479
# par = [1.500000, 0.400000, 0.031695, 0.126163, 0.650000, 0.100000]
# print(data[0:5,])
#
# normalize_space(stims)
# print(stims)


#ps, db = do_bns(par, [trial_num, optimizing, evaluating, logging, 1], data)


