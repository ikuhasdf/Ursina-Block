from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
from ursina.prefabs.ursfx import ursfx
import random
import time

app = Ursina()

# 加载纹理
grass_texture = load_texture('assets/Grass_block.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
unknown_texture = load_texture('assets/无标题.png')
arm_texture = load_texture('assets/arm_texture.png')
wolf_texture = load_texture('assets/wolf.png')
wolf_model = load_model('assets/狼.glb')

# 播放音频
try:
    audio = Audio('assets/Tite.mp3', loop=True, autoplay=True)
except:
    print("音频文件未找到，不影响游戏运行")

block_pick = 1

# 方块纹理映射（不变）
texture_mapping = {
    1: grass_texture,
    2: stone_texture,
    3: brick_texture,
    4: dirt_texture,
    5: unknown_texture,
    6: None
}

MAX_PLAYER_SPEED = 20

def update():
    global block_pick
    # 选择方块
    for i in range(1, 7):
        if held_keys[str(i)]:
            block_pick = i

    # 手的动作
    if held_keys['left mouse down'] or held_keys['right mouse down']:
        hand.active()
    else:
        hand.passive()

    # 射击
    if held_keys['q']:
        shoot()

    # 怪物行为
    if 'wolf' in locals():
        wolf.look_at(player.position)
        distance = ((wolf.x - player.x) **2 + (wolf.z - player.z)** 2) **0.5
        if distance > 2:
            wolf.position += wolf.forward * time.dt * 2

    # 玩家加速
    if held_keys['y'] and player.speed < MAX_PLAYER_SPEED:
        player.speed += 0.1  # 从+1改为+0.1，每秒增加约6
    elif not held_keys['y'] and player.speed > 9:  # 松开后减速回默认
        player.speed -= 0.1

random_seed = random.randint(1, 2038)
sky_texture = load_texture("skybox.png")

class Block(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='assets/block', 
            origin_y=0.5,
            texture=texture,
            scale=0.5,
            color=color.color(0, 0, random.uniform(0.9, 1))
        )

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                texture = texture_mapping.get(block_pick)
                if texture:
                    Block(position=self.position + mouse.normal, texture=texture)
            if key == 'left mouse down':
                destroy(self)

class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=10000,
            double_sided=True
        )

class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='assets/arm.obj',  
            texture=arm_texture,
            scale=0.2,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.6)
        )

    def active(self):
        self.position = Vec2(0.3, -0.5)

    def passive(self):
        self.position = Vec2(0.4, -0.6)

class Wolf(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=scene,
            model=wolf_model,
            position=(random.randint(0, 12), 3, random.randint(0, 12)),
            texture=wolf_texture,
            scale_y=2,
            origin_y=0.5,
            double_sided=True,
            collider="box"
        )
        self.health_bar = Entity(parent=self, model='cube', color=color.red, y=1.2, scale=(1.5, 0.1, 0.1))
        self.max_hp = 100
        self.hp = self.max_hp

def input(key):
    if key == 'escape':
        quit()

# 保留你的玩家模型
try:
    player = FirstPersonController(collider="box", speed=9, model='jjjj.glb', color=color.orange)
except:
    player = FirstPersonController(collider="box", speed=9, model='cube', color=color.orange)  # 备选方案

hand = Hand()
gun = Entity(model='quad', parent=hand, z=1, color=color.yellow, enabled=False)

def shoot():
    ursfx([(0.0, 0.0), (0.1, 0.5), (0.2, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
    gun.enabled = True
    invoke(setattr, gun, 'enabled', False, delay=0.1)


noise = PerlinNoise(octaves=3, seed=random_seed)
for z in range(40):
    for x in range(40):
        y = floor(noise([x / 24, z / 24]) * 10)

        Block(position=(x, y, z), texture=texture_mapping[1])
        for i in range(-1, y):
            Block(position=(x, i, z), texture=texture_mapping[2])

sky1 = Sky()
wolf = Wolf()

print(f"种子是（{random_seed}）")

app.run()