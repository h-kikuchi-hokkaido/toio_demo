from dataclasses import dataclass
from toio.cube import ToioCoreCube


import asyncio

@dataclass
class Point:
    x: int
    y: int

@dataclass
class MapSize:
    xmin: int
    xmax: int
    ymin: int
    ymax: int
    
@dataclass
class Goal:
    xmin: int
    xmax: int
    ymin: int
    ymax: int

class SavePoint:
    def __init__(self):
        self.old_pos = list()
        self.collision_pos = list()
        
    def set_current_pos(self,point:Point):
        if point is not None:
            self.current_pos = point

    def get_current_pos(self):
        return self.current_pos

    def get_old_pos(self):
        return self.old_pos
    
       
    def get_collision_pos(self):
        return self.collision_pos
    
    def update_old_pos(self):
        self.old_pos.append(self.current_pos)

    def update_collision_pos(self):
        self.collision_pos.append(self.current_pos)

class MyCube:
    def __init__(self,cube:ToioCoreCube,map_size:MapSize,goal:Goal):
        self.cube = cube
        self.map_size = map_size
        self.goal = goal
        self.flag=False
        self.w_flag=False

    async def current_pos(self):
        data = await self.cube.api.id_information.read()
        try:
            return Point(data.center.point.x,data.center.point.y)
        except:
            return None
        
       
    async def current_angle(self):
        data = await self.cube.api.id_information.read()
        try:
            return data.center.angle
        except:
            return None

    async def forward(self):
        await self.cube.api.motor.motor_control(10, 10)
        await asyncio.sleep(1)
        await self.cube.api.motor.motor_control(0, 0)
        self.flag=True
        self.w_flag=True

    async def backward(self):
        await self.cube.api.motor.motor_control(-10, -10)
        await asyncio.sleep(1)
        await self.cube.api.motor.motor_control(0, 0)
        self.flag=True
        self.w_flag=False

    async def turn_right(self):
        await self.cube.api.motor.motor_control(10, -10)
        await asyncio.sleep(0.2)
        await self.cube.api.motor.motor_control(0, 0)
        self.flag=False
        self.w_flag=False
    
    async def turn_left(self): 
        await self.cube.api.motor.motor_control(-10, 10)
        await asyncio.sleep(0.2)
        await self.cube.api.motor.motor_control(0, 0)
        self.flag=False
        self.w_flag=False

    async def stop(self):
        await self.cube.api.motor.motor_control(0, 0)
        self.flag=False
        self.w_flag=False

    async def is_collision(self):
        pass
        

    async def is_in_goal(self):
        current_pos = await self.current_pos()
        if current_pos is None:
            return False
        if self.goal.xmin <= current_pos.x <= self.goal.xmax and self.goal.ymin <= current_pos.y <= self.goal.ymax:
            return True
        else:
            return False
        
    async def is_out_map(self):
        current_pos = await self.current_pos()
        if current_pos is None:
            return False
        if self.map_size.xmin <= current_pos.x <= self.map_size.xmax and self.map_size.ymin <= current_pos.y <= self.map_size.ymax:
            return False
        else:
            return True
           

class ToioDo:
    def __init__(self,points:SavePoint,cube:MyCube):
        self.savepoint = points
        self.cube = cube
    
    async def store_current_pos(self):
        current_pos = await self.cube.current_pos()
        self.savepoint.set_current_pos(current_pos)        
        return current_pos

    
    async def update(self):
        await self.store_current_pos()
        old_pos = self.savepoint.get_old_pos()
        if await self.cube.current_pos() == old_pos[-1]:
            self.savepoint.update_collision_pos()
            await self.cube.backward()
            await self.cube.turn_right()
    
    async def update_savepoint(self):
        await self.store_current_pos()
        self.savepoint.update_old_pos()
        self.savepoint.update_collision_pos()
        

    