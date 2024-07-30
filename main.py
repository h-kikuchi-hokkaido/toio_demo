from toio_point_data import *
import asyncio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from toio import *

MAPSIZE = MapSize(34, 339, 35, 250)
GOAL = Goal(34,84,35,85)



cube = ToioCoreCube()

async def scan_and_connect():
   
    await cube.scan()
    await cube.connect()

    await asyncio.sleep(1)

    return cube


async def loop(toiodo: ToioDo, ax):
    while True:
        if await toiodo.cube.is_in_goal() or await toiodo.cube.is_out_map():
            await toiodo.cube.stop()
            break
        await toiodo.cube.forward()
        
        while True:            
            current_pos = await toiodo.store_current_pos()
            if current_pos is None:
                continue
            toiodo.savepoint.update_old_pos()
            
            
            
            plt.plot(current_pos.x, current_pos.y, marker='o', c='r')
            plt.pause(0.1)

            old_pos = toiodo.savepoint.get_old_pos()
            await asyncio.sleep(0.1)

            if len(old_pos) > 1:
                if toiodo.savepoint.get_old_pos()[-1] == toiodo.savepoint.get_old_pos()[-2]:
                    rect2 = patches.Rectangle((current_pos.x, current_pos.y), 8, 8, 
                                              edgecolor='blue', facecolor='blue', linewidth=2 )
                    ax.add_patch(rect2)
                    break
        
        await toiodo.cube.backward()
        if random.randint(1,10) % 2 == 0:
            await toiodo.cube.turn_right()
        else:
            await toiodo.cube.turn_left()

        #await toiodo.update()
        # await asyncio.sleep(0.08)
        # print(toiodo.savepoint.get_current_pos())
        # print(toiodo.savepoint.get_old_pos()[-1])
        # print(toiodo.savepoint.get_collision_pos())
        
async def point_loop(toiodo: ToioDo, ax):
    while True:
        if await toiodo.cube.is_in_goal() or await toiodo.cube.is_out_map():
            break
        while True:
            await toiodo.update_savepoint()
            await asyncio.sleep(0.1)

async def move_loop(toiodo: ToioDo, ax):   
    while True:
        if await toiodo.cube.is_in_goal() or await toiodo.cube.is_out_map():
            await toiodo.cube.stop()
            break
        await toiodo.cube.forward()
        
        while True:            
            current_pos = await toiodo.store_current_pos()
            if current_pos is None:
                continue
            
            
            
            plt.plot(current_pos.x, current_pos.y, marker='o', c='r')
            plt.pause(0.1)

            old_pos = toiodo.savepoint.get_old_pos()
            await asyncio.sleep(0.1)

            if len(old_pos) > 1:
                if toiodo.savepoint.get_old_pos()[-1] == toiodo.savepoint.get_old_pos()[-2]:
                    rect2 = patches.Rectangle((current_pos.x, current_pos.y), 8, 8, 
                                              edgecolor='blue', facecolor='blue', linewidth=2 )
                    ax.add_patch(rect2)
                    break
        
        await toiodo.cube.backward()
        if random.randint(1,10) % 2 == 0:
            await toiodo.cube.turn_right()
        else:
            await toiodo.cube.turn_left()





def map_plot(mapsize: MapSize,ax):
    
    plt.title("Realtime Display")
    plt.xlim(mapsize.xmin, mapsize.xmax)
    plt.ylim(mapsize.ymin, mapsize.ymax)
    ax.invert_xaxis()
    ax.invert_yaxis()


async def main():
    cube = await scan_and_connect()
    mycube = MyCube(cube, MAPSIZE, GOAL)
    savepoint = SavePoint()
    toiodo = ToioDo(savepoint, mycube)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    
    map_plot(MAPSIZE,ax) 
    await loop(toiodo, ax)
    plt.savefig("map.png")
    



if __name__ == "__main__":
    asyncio.run(main())
