#!/usr/bin/env python3
"""
Blender Python API script to generate a .blend file programmatically.
Run this inside Blender: blender --background --python generate_blend.py
"""

import bpy
import math
import random
import os

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        bpy.data.textures.remove(block)
    for block in bpy.data.images:
        bpy.data.images.remove(block)

def create_material(name, color, emission_strength=0.0, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = (*color, 1.0)
    principled.inputs['Metallic'].default_value = metallic
    principled.inputs['Roughness'].default_value = roughness
    if emission_strength > 0:
        principled.inputs['Emission Strength'].default_value = emission_strength
        principled.inputs['Emission Color'].default_value = (*color, 1.0)
    
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_fractal_tree(name, location, scale, depth, angle_spread, branch_factor):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    def add_branch(parent_loc, parent_rot, length, thickness, current_depth):
        if current_depth >= depth:
            return
        
        bpy.ops.mesh.primitive_cone_add(
            vertices=8,
            radius1=thickness,
            radius2=thickness * 0.7,
            depth=length,
            location=parent_loc,
            rotation=parent_rot
        )
        obj = bpy.context.active_object
        obj.name = f"{name}_branch_{current_depth}"
        collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)
        
        tip_loc = (
            parent_loc[0] + math.sin(parent_rot[2]) * math.cos(parent_rot[0]) * length,
            parent_loc[1] - math.cos(parent_rot[2]) * math.cos(parent_rot[0]) * length,
            parent_loc[2] + math.sin(parent_rot[0]) * length
        )
        
        num_branches = max(1, int(branch_factor * (1 - current_depth / depth)))
        for i in range(num_branches):
            new_angle = parent_rot[2] + random.uniform(-angle_spread, angle_spread)
            new_pitch = parent_rot[0] + random.uniform(-angle_spread * 0.5, angle_spread * 0.5)
            new_rot = (new_pitch, 0, new_angle)
            
            new_length = length * random.uniform(0.6, 0.85)
            new_thickness = thickness * random.uniform(0.6, 0.8)
            
            add_branch(tip_loc, new_rot, new_length, new_thickness, current_depth + 1)
    
    add_branch(location, (0, 0, 0), scale * 2.0, scale * 0.15, 0)

def create_particle_field(name, count, bounds, colors):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    for i in range(count):
        x = random.uniform(-bounds[0], bounds[0])
        y = random.uniform(-bounds[1], bounds[1])
        z = random.uniform(-bounds[2], bounds[2])
        
        size = random.uniform(0.02, 0.15)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=size, location=(x, y, z))
        obj = bpy.context.active_object
        obj.name = f"{name}_particle_{i}"
        collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)
        
        color = random.choice(colors)
        mat = create_material(f"{name}_mat_{i}", color, emission_strength=random.uniform(0.5, 3.0))
        obj.data.materials.append(mat)

def create_geometric_landscape(name, grid_size, height_scale):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    verts = []
    faces = []
    
    for gx in range(grid_size):
        for gy in range(grid_size):
            x = (gx - grid_size // 2) * 1.0
            y = (gy - grid_size // 2) * 1.0
            
            noise_val = 0
            for octave in range(4):
                freq = 2 ** octave
                amp = 0.5 ** octave
                noise_val += amp * (
                    math.sin(x * 0.1 * freq + gx * 0.7) * 
                    math.cos(y * 0.1 * freq + gy * 0.3) +
                    math.sin((x + y) * 0.05 * freq) * 0.5
                )
            
            z = noise_val * height_scale
            verts.append((x, y, z))
    
    for gx in range(grid_size - 1):
        for gy in range(grid_size - 1):
            a = gx * grid_size + gy
            b = (gx + 1) * grid_size + gy
            c = (gx + 1) * grid_size + (gy + 1)
            d = gx * grid_size + (gy + 1)
            faces.append((a, b, c, d))
    
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    
    mat = create_material(f"{name}_material", (0.2, 0.4, 0.1), roughness=0.8)
    obj.data.materials.append(mat)
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    
    return obj

def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.data.color = (1.0, 0.95, 0.8)
    
    bpy.ops.object.light_add(type='AREA', location=(-5, 5, 10))
    area = bpy.context.active_object
    area.data.energy = 50.0
    area.data.color = (0.2, 0.4, 1.0)
    area.data.size = 10.0
    
    bpy.ops.object.light_add(type='POINT', location=(0, -10, 5))
    point = bpy.context.active_object
    point.data.energy = 100.0
    point.data.color = (1.0, 0.3, 0.1)

def setup_camera():
    bpy.ops.object.camera_add(location=(15, -15, 10), rotation=(1.1, 0, 0.8))
    cam = bpy.context.active_object
    cam.data.lens = 35
    cam.data.clip_start = 0.1
    cam.data.clip_end = 200
    bpy.context.scene.camera = cam

def setup_world():
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    nodes.clear()
    
    background = nodes.new('ShaderNodeBackground')
    background.inputs['Color'].default_value = (0.02, 0.02, 0.05, 1.0)
    background.inputs['Strength'].default_value = 0.1
    
    output = nodes.new('ShaderNodeOutputWorld')
    links.new(background.outputs['Background'], output.inputs['Surface'])

def animate_objects():
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and 'particle' in obj.name.lower():
            obj.animation_data_create()
            action = bpy.data.actions.new(name=f"{obj.name}_action")
            obj.animation_data.action = action
            
            fcurve_x = action.fcurves.new(data_path="location", index=0)
            fcurve_y = action.fcurves.new(data_path="location", index=1)
            fcurve_z = action.fcurves.new(data_path="location", index=2)
            
            for frame in range(1, 251):
                t = frame / 250.0 * 4 * math.pi
                fcurve_x.keyframe_points.insert(frame, obj.location.x + math.sin(t + obj.location.y) * 0.5)
                fcurve_y.keyframe_points.insert(frame, obj.location.y + math.cos(t + obj.location.x) * 0.5)
                fcurve_z.keyframe_points.insert(frame, obj.location.z + math.sin(t * 0.5) * 0.3)

def main():
    clear_scene()
    setup_world()
    setup_lighting()
    setup_camera()
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250
    
    colors_fire = [(1.0, 0.3, 0.0), (1.0, 0.6, 0.0), (1.0, 0.9, 0.1), (1.0, 1.0, 0.5)]
    colors_ocean = [(0.0, 0.2, 0.6), (0.0, 0.4, 0.8), (0.2, 0.6, 1.0), (0.5, 0.8, 1.0)]
    colors_forest = [(0.1, 0.4, 0.1), (0.2, 0.6, 0.2), (0.3, 0.8, 0.3), (0.5, 1.0, 0.5)]
    colors_crystal = [(0.8, 0.9, 1.0), (0.6, 0.8, 1.0), (0.9, 0.7, 1.0), (1.0, 0.9, 0.7)]
    
    create_fractal_tree("Tree_Fire", (-8, -5, 0), 1.0, 6, 0.8, 2.5)
    tree_fire = bpy.data.collections["Tree_Fire"]
    for obj in tree_fire.objects:
        mat = create_material("Bark_Fire", (0.3, 0.15, 0.05), roughness=0.9)
        obj.data.materials.append(mat)
    
    create_fractal_tree("Tree_Ice", (8, 5, 0), 1.2, 7, 0.6, 2.0)
    tree_ice = bpy.data.collections["Tree_Ice"]
    for obj in tree_ice.objects:
        mat = create_material("Bark_Ice", (0.6, 0.8, 1.0), emission_strength=0.5, roughness=0.1, metallic=0.8)
        obj.data.materials.append(mat)
    
    create_particle_field("Fireflies", 200, (15, 15, 10), colors_fire + colors_ocean)
    create_particle_field("Spores", 150, (12, 12, 8), colors_forest)
    create_particle_field("Crystals", 100, (10, 10, 6), colors_crystal)
    
    landscape = create_geometric_landscape("Landscape", 60, 3.0)
    
    animate_objects()
    
    output_path = os.path.expanduser("~/ailetloos_generated.blend")
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()