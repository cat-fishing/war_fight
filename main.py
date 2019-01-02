import pygame
import sys
import traceback
from myplane import *
import enemy
import bullet
import supply
from pygame.locals import *
from random import *


pygame.init()
pygame.mixer.init()
bg_size = width, height = 480, 700
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption("飞机大战 -- Cat-fishing")
background = pygame.image.load("images/background.png").convert()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 载入游戏音乐
pygame.mixer.music.load("sound/game_music.ogg")
pygame.mixer.music.set_volume(0.2)
bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
bullet_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2)
supply_sound = pygame.mixer.Sound("sound/supply.wav")
supply_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav")
get_bullet_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound("sound/upgrade.wav")
upgrade_sound.set_volume(0.2)
enemy3_fly_sound = pygame.mixer.Sound("sound/enemy3_flying.wav")
enemy3_fly_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.2)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.5)
me_down_sound = pygame.mixer.Sound("sound/me_down.wav")
me_down_sound.set_volume(0.2)


def add_small_enemies(group1, group2, num):
    for i in range(num):
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)


def add_mid_enemies(group1, group2, num):
    for i in range(num):
        e2 = enemy.MidEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)


def add_big_enemies(group1, group2, num):
    for i in range(num):
        e3 = enemy.BigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)


def main():
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    running = True
    me = MyPlane(bg_size)
    # 得分
    score = 0
    score_font = pygame.font.Font("font/font.TTF", 36)
    enemies = pygame.sprite.Group()
    # 生成地方小飞机
    small_enemies = pygame.sprite.Group()
    add_small_enemies(small_enemies, enemies, 15)
    # 生成地方中型飞机
    mid_enemies = pygame.sprite.Group()
    add_mid_enemies(mid_enemies, enemies, 4)
    # 生成地方大型飞机
    big_enemies = pygame.sprite.Group()
    add_big_enemies(big_enemies, enemies, 2)
    switch_image = True
    delay = 100

    # 生成子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 4

    # 中弹图片索引
    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    me_destroy_index = 0

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        # 检测用户键盘操作
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_w] or key_pressed[K_UP]:
            me.moveUp()
        if key_pressed[K_s] or key_pressed[K_DOWN]:
            me.moveDown()
        if key_pressed[K_a] or key_pressed[K_LEFT]:
            me.moveLeft()
        if key_pressed[K_d] or key_pressed[K_RIGHT]:
            me.moveRight()

        screen.blit(background, (0, 0))

        if me.active:
            # 绘制我方飞机
            if switch_image:
                screen.blit(me.image1, me.rect)
            else:
                screen.blit(me.image2, me.rect)
        else:
            # 毁灭
            if not (delay % 3):
                if me_destroy_index == 0:
                    me_down_sound.play()
                screen.blit(me.destroy_images[me_destroy_index], me.rect)
                me_destroy_index = (me_destroy_index + 1) % 4
                if me_destroy_index == 0:
                    print("Game Over!")
                    running = False

        for i in range(BULLET1_NUM):
            bullet1.append(bullet.Bullet1(me.rect.midtop))

        # 每10帧发射一枚子弹
        if not(delay % 10):
            bullet_sound.play()
            bullet1[bullet1_index].reset(me.rect.midtop)
            bullet1_index = (bullet1_index + 1) % BULLET1_NUM

        # 检测子弹与敌机碰撞
        for each in bullet1:
            if each.active:
                each.move()
                screen.blit(each.image, each.rect)
                enemy_hit = pygame.sprite.spritecollide(each, enemies, False, pygame.sprite.collide_mask)
                if enemy_hit:
                    each.active = False
                    for e in enemy_hit:
                        if e in mid_enemies or e in big_enemies:
                            e.energy -= 1
                            if e.energy == 0:
                                if e in mid_enemies:
                                    score += 6000
                                elif e in big_enemies:
                                    score += 10000
                                e.active = False
                        else:
                            score += 1000
                            e.active = False

        # 绘制大型敌机
        for each in big_enemies:
            if each.active:
                each.move()
                if each.hit:
                    screen.blit(each.image_hit, each.rect)
                    each.hit = False
                else:
                    if switch_image:
                        screen.blit(each.image1, each.rect)
                    else:
                        screen.blit(each.image2, each.rect)
                # 绘制血槽
                pygame.draw.line(screen, BLACK, (each.rect.left, each.rect.top - 5),
                                 (each.rect.right, each.rect.top - 5), 2)
                # 当生命大于20%显示绿色，否则显示红色
                energy_remain = each.energy / enemy.BigEnemy.energy
                if energy_remain > 0.2:
                    energy_color = GREEN
                else:
                    energy_color = RED

                pygame.draw.line(screen, energy_color, (each.rect.left, each.rect.top - 5),
                                 (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5), 2)

                # 播放音效
                if each.rect.bottom > -50:
                    enemy3_fly_sound.play()
            else:
                if not (delay % 3):
                    if e3_destroy_index == 0:
                        enemy3_down_sound.play()
                    screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                    e3_destroy_index = (e3_destroy_index + 1) % 4
                    if e3_destroy_index == 0:
                        enemy3_fly_sound.stop()
                        each.reset()
        # 绘制中型敌机
        for each in mid_enemies:
            if each.active:
                each.move()
                if each.hit:
                    screen.blit(each.image_hit, each.rect)
                else:
                    screen.blit(each.image, each.rect)
                # 绘制血槽
                pygame.draw.line(screen, BLACK, (each.rect.left, each.rect.top - 5),
                                 (each.rect.right, each.rect.top - 5), 2)
                # 当生命大于20%显示绿色，否则显示红色
                energy_remain = each.energy / enemy.MidEnemy.energy
                if energy_remain > 0.2:
                    energy_color = GREEN
                else:
                    energy_color = RED

                pygame.draw.line(screen, energy_color, (each.rect.left, each.rect.top - 5),
                                 (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5), 2)
            else:
                if not (delay % 3):
                    if e2_destroy_index == 0:
                        enemy2_down_sound.play()
                    screen.blit(each.destroy_images[e2_destroy_index], each.rect)
                    e2_destroy_index = (e2_destroy_index + 1) % 4
                    if e2_destroy_index == 0:
                        each.reset()

        # 绘制小型敌机
        for each in small_enemies:
            if each.active:
                each.move()
                screen.blit(each.image, each.rect)
            else:
                if not (delay % 3):
                    if e1_destroy_index == 0:
                        enemy1_down_sound.play()
                    screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                    e1_destroy_index = (e1_destroy_index + 1) % 4
                    if e1_destroy_index == 0:
                        each.reset()

        # 检测敌我飞机是否相撞
        enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
        if enemies_down:
            me.active = False
            for e in enemies_down:
                e.active = False

        # 绘制得分
        score_text = score_font.render("Score: %s" % str(score), True, WHITE)
        screen.blit(score_text, (10, 5))

        # 切换图片
        if not (delay % 5):
            switch_image = not switch_image
        delay -= 1
        if not delay:
            delay = 100
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
