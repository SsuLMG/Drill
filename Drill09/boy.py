# 이것은 각 상태들을 객체로 구현한 것임.
import math
import random

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a



def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def time_out(e):
    return e[0] == 'TIME_OUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def autokey(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def time_out(e):
    return e[0] == 'TIME_OUT'

def Lerp(A, B, Alpha):
    return A * (1 - Alpha) + B * Alpha


class Idle:
    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.start_time = get_time()
        print('Idle Enter')

    @staticmethod
    def exit(boy, e):
        print('Idle Exit')

    @staticmethod
    def do(boy):
        if get_time() - boy.start_time > 3.0:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)



class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle
        self.table = {
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, autokey: AutoRun},
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, autokey: AutoRun},
            Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle, autokey: AutoRun},
            AutoRun: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, time_out: Idle}
        }

    def handle_event(self, e):  # space handle event
        for check_event, next_state in self.table[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True # 성공적으로 이벤트 변환
        return False # 이벤트를 소모하지 못함

    def start(self):
        self.cur_state.enter(self.boy, ('START', 0))

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 0
        self.speed = 3
        self.time = 0.0
        self.dir = 0
        self.body_size = 100
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        #pico2d event -> handle event
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()


class Sleep:
    @staticmethod
    def enter(boy, e):
        print('Sleep Enter')

    @staticmethod
    def exit(boy, e):
        print('Sleep Exit')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100, -math.pi / 2, '', boy.x + 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100, math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)


class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):  # 오른쪽으로 RUN
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e):  # 왼쪽으로 RUN
            boy.dir, boy.action = -1, 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class AutoRun:
    time = 0
    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.dir = -1
        elif boy.action == 1:
            boy.dir = 1
        elif boy.action == 2:
            boy.action = 0
            boy.dir = -1
        elif boy.action == 3:
            boy.action = 1
            boy.dir = 1

        boy.frame = 0
        boy.speed = 20
        AutoRun.time = get_time()
        boy.body_size = 150
        print('auto enter')

    @staticmethod
    def do(boy):
        if boy.x < 10:
            boy.dir, boy.action = 1, 1
        elif boy.x > 800:
            boy.dir, boy.action = -1,0

        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.speed * boy.dir

        if get_time() - AutoRun.time >= 5.0:
            boy.state_machine.handle_event(('TIME_OUT', 0))
            print('time out')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, 100 * boy.action, 100, 100, boy.x, boy.y + 20, boy.body_size, boy.body_size)


    @staticmethod
    def exit(boy, e):
        boy.speed = 5
        boy.body_size = 100
        boy.y = 90
        boy.dir = 0
        print('auto exit')