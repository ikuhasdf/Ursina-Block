from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
from ursina.prefabs.ursfx import ursfx
import random
import time

app = Ursina()

# 完整设置窗口
window.title = f"miniworld"
window.borderless = False  # 有边框
window.fullscreen = False  # 不全屏
window.size = (1280, 720)  # 窗口大小
window.position = (100, 100)
window.exit_button.visible = False  # 隐藏默认退出按钮

# 加载纹理
grass_texture = load_texture('assets/Grass_block.png')
stone_texture = load_texture('assets/stone.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
unknown_texture = load_texture('assets/diamond_block.png')
arm_texture = load_texture('assets/arm_texture.png')
diamond_ore = load_texture('assets/diamond_ore.png')
lapis_ore = load_texture('assets/lapis_ore.png')
iron_ore = load_texture('assets/iron_ore.png')
blackcrystal = load_texture('assets/blackcrystal.png')
sand = load_texture('assets/sand.png')
# 创建简单的小猪模型 - 简化版本
def create_pig_model():
    """创建一个简化的小猪模型"""
    # 使用简单的立方体组合
    return 'cube'  # 暂时使用立方体


# 创建小猪模型
pig_model = create_pig_model()

# 游戏状态
game_started = False

# 方块纹理映射
texture_mapping = {
    1: grass_texture,
    2: stone_texture,
    3: brick_texture,
    4: dirt_texture,
    5: unknown_texture,
    6: diamond_ore,
    7:lapis_ore,
    8:iron_ore,
    9:blackcrystal,
    0:sand
}

MAX_PLAYER_SPEED = 20
VOID_HEIGHT = -65  # 虚空高度

# 全局变量
block_pick = 1
block_pool = []
player = None
hand = None
sky1 = None
random_seed = None
pigs = []  # 存储所有小猪的列表


def create_main_menu():
    """创建主菜单"""
    # 背景
    background = Entity(
        model='quad',
        scale=(2, 2),
        texture='skybox.png',
        parent=camera.ui
    )

    # 标题
    title = Text(
        text="MINIWORLD Community Editon",
        scale=3,
        y=0.3,
        origin=(0, 0),
        color=color.yellow,
        background=True
    )

    # 开始游戏按钮和文字
    start_button = Button(
        text=' ',  # 空文本
        color=color.green,
        scale=(0.3, 0.1),
        y=0,
        parent=camera.ui
    )
    start_text = Text(
        text='开始游戏',
        parent=start_button,
        scale=2,
        y=0,
        z=-0.1,
        color=color.white
    )

    # 退出游戏按钮和文字
    quit_button = Button(
        text=' ',  # 空文本
        color=color.red,
        scale=(0.3, 0.1),
        y=-0.2,
        parent=camera.ui
    )
    quit_text = Text(
        text='退出游戏',
        parent=quit_button,
        scale=2,
        y=0,
        z=-0.1,
        color=color.white
    )

    def start_game():
        global game_started
        game_started = True
        # 移除菜单元素
        destroy(background)
        destroy(title)
        destroy(start_button)
        destroy(start_text)
        destroy(quit_button)
        destroy(quit_text)
        # 初始化游戏
        init_game()

    def quit_game():
        application.quit()

    start_button.on_click = start_game
    quit_button.on_click = quit_game


def init_game():
    """初始化游戏"""
    global player, hand, sky1, block_pool, random_seed, pigs

    # 播放音频
    try:
        audio = Audio('assets/bgm_day_1.ogg', loop=True, autoplay=True)
    except:
        print("音频文件未找到，不影响游戏运行")

    # 生成随机种子
    random_seed = random.randint(1, 2038)

    # 创建玩家
    try:
        player = FirstPersonController(collider="box", speed=9, model='jjjj.glb', color=color.orange)
    except:
        player = FirstPersonController(collider="box", speed=9, model='cube', color=color.orange)

    hand = Hand()

    # 生成地形
    noise = PerlinNoise(octaves=3, seed=random_seed)
    ground_positions = {}  # 记录地面位置

    for z in range(30):
        for x in range(30):
            y = floor(noise([x / 24, z / 24]) * 8)
            ground_positions[(x, z)] = y

            Block(position=(x, y, z), texture=texture_mapping[1])
            # 减少地下方块层数
            for i in range(max(-1, y - 3), y):
                Block(position=(x, i, z), texture=texture_mapping[2])

    sky1 = Sky()

    # 生成小猪
    spawn_pigs(5, ground_positions)  # 生成5只小猪

    print(f"种子是（{random_seed}）")


def spawn_pigs(count, ground_positions=None):
    """生成指定数量的小猪"""
    global pigs
    pigs = []

    for i in range(count):
        # 随机位置（在地面上）
        x = random.uniform(5, 25)
        z = random.uniform(5, 25)
        y = find_ground_height(x, z, ground_positions) + 1  # 在地面之上1个单位

        pig = Pig(position=(x, y, z))
        pigs.append(pig)
        print(f"生成小猪在位置 ({x:.1f}, {y:.1f}, {z:.1f})")


def find_ground_height(x, z, ground_positions=None):
    """找到指定坐标的地面高度"""
    if ground_positions:
        # 找到最近的整数坐标
        nearest_x = round(x)
        nearest_z = round(z)
        if (nearest_x, nearest_z) in ground_positions:
            return ground_positions[(nearest_x, nearest_z)]
    # 默认返回固定高度
    return 2


class Pig(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            model=pig_model,
            color=color.pink,  # 粉色小猪
            position=position,
            scale=0.5,
            collider='box'
        )
        self.speed = 0.5  # 降低速度
        self.direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
        self.move_timer = 0
        self.idle_timer = 0
        self.state = "wandering"  # wandering, idle
        print(f"创建粉色小猪")

        # 添加小猪的细节部件
        self.create_pig_details()

    def create_pig_details(self):
        """为小猪添加细节部件"""
        # 头部
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.pink,
            scale=(0.6, 0.4, 0.4),
            position=(0.3, 0.2, 0)
        )

        # 耳朵
        self.ear_left = Entity(
            parent=self.head,
            model='cube',
            color=color.pink.tint(-0.2),
            scale=(0.2, 0.1, 0.1),
            position=(-0.2, 0.2, 0.1),
            rotation=(0, 0, 30)
        )

        self.ear_right = Entity(
            parent=self.head,
            model='cube',
            color=color.pink.tint(-0.2),
            scale=(0.2, 0.1, 0.1),
            position=(-0.2, 0.2, -0.1),
            rotation=(0, 0, -30)
        )

        # 腿
        leg_scale = (0.1, 0.3, 0.1)
        self.leg_front_left = Entity(
            parent=self,
            model='cube',
            color=color.pink.tint(-0.3),
            scale=leg_scale,
            position=(-0.2, -0.3, 0.15)
        )

        self.leg_front_right = Entity(
            parent=self,
            model='cube',
            color=color.pink.tint(-0.3),
            scale=leg_scale,
            position=(-0.2, -0.3, -0.15)
        )

        self.leg_back_left = Entity(
            parent=self,
            model='cube',
            color=color.pink.tint(-0.3),
            scale=leg_scale,
            position=(0.2, -0.3, 0.15)
        )

        self.leg_back_right = Entity(
            parent=self,
            model='cube',
            color=color.pink.tint(-0.3),
            scale=leg_scale,
            position=(0.2, -0.3, -0.15)
        )

        # 尾巴
        self.tail = Entity(
            parent=self,
            model='cube',
            color=color.pink.tint(-0.2),
            scale=(0.05, 0.05, 0.2),
            position=(0.4, 0, 0),
            rotation=(0, 0, 45)
        )

    def update(self):
        if not game_started:
            return

        self.move_timer += time.dt
        self.idle_timer += time.dt

        # 状态机
        if self.state == "wandering":
            self.wander()
        elif self.state == "idle":
            self.idle()

        # 防止小猪掉下世界
        if self.y < -10:
            self.y = 10

    def wander(self):
        """漫游行为"""
        # 移动
        new_position = self.position + self.direction * self.speed * time.dt

        # 简单的边界检查
        if 0 <= new_position.x <= 30 and 0 <= new_position.z <= 30:
            self.position = new_position

        # 随机改变方向
        if self.move_timer > random.uniform(2, 5):
            self.direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()
            self.move_timer = 0

            # 随机切换到 idle 状态
            if random.random() < 0.3:
                self.state = "idle"
                self.idle_timer = 0

    def idle(self):
        """idle 状态，小猪站着不动"""
        if self.idle_timer > random.uniform(1, 3):
            self.state = "wandering"
            self.move_timer = 0


def update():
    global block_pick
    if not game_started:
        return

    # 选择方块
    for i in range(0, 9):
        if held_keys[str(i)]:
            block_pick = i

    # 手的动作
    if held_keys['left mouse down'] or held_keys['right mouse down']:
        hand.active()
    else:
        hand.passive()

    # 检测是否掉入虚空
    if player and player.y < VOID_HEIGHT:
        print("你掉入了虚空！游戏结束")
        application.quit()


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
        # 添加到池中
        block_pool.append(self)

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                texture = texture_mapping.get(block_pick)
                if texture:
                    Block(position=self.position + mouse.normal, texture=texture)
            if key == 'left mouse down':
                # 从池中移除并销毁
                if self in block_pool:
                    block_pool.remove(self)
                destroy(self)


class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture='skybox.png',
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


def input(key):
    if key == 'escape':
        if game_started:
            # 游戏运行时按ESC退出游戏
            application.quit()
        else:
            # 菜单时按ESC退出程序
            application.quit()


# 创建主菜单
create_main_menu()

app.run()
