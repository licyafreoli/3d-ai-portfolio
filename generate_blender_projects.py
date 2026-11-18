import bpy, math, json, os, time
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parent / '3d_projects'
ROOT.mkdir(exist_ok=True)
RES = (900, 675)

def reset_scene(name):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.materials:
        if block.users == 0: bpy.data.materials.remove(block)
    scene = bpy.context.scene
    scene.name = name
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 20
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.world.color = (0.035, 0.045, 0.06)
    scene.render.image_settings.color_depth = '8'
    return scene

def material(name, color, metallic=0.0, roughness=0.35, emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = roughness
    if emission is not None:
        if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value = (*emission, 1)
        elif 'Emission' in bs.inputs: bs.inputs['Emission'].default_value = (*emission, 1)
        if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value = emission_strength
    return m

def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

def bevel(obj, width=.06, segments=3):
    mod = obj.modifiers.new('Edge highlights', 'BEVEL')
    mod.width = width
    mod.segments = segments
    norm = obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def cube(name, loc, scale, mat, edge=.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, mat)
    if edge: bevel(o, edge, 3)
    return o

def cyl(name, loc, radius, depth, mat, vertices=48, bevel_width=.02, direction=(0,0,1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0,0,1)).rotation_difference(Vector(direction).normalized())
    assign(o, mat)
    if bevel_width: bevel(o, bevel_width, 2)
    return o

def sphere(name, loc, scale, mat, seg=24, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, mat)
    return o

def torus(name, loc, major, minor, mat, direction=(0,0,1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=48, minor_segments=12, location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0,0,1)).rotation_difference(Vector(direction).normalized())
    assign(o, mat)
    return o

def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()

def camera(loc, target, lens=55):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.name = 'Camera_Main'
    aim(c, target)
    c.data.lens = lens
    bpy.context.scene.camera = c
    return c

def area(name, loc, target, power, color, size, shape='DISK'):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.color = color
    o.data.shape = shape
    o.data.size = size
    aim(o, target)
    return o

def world_color(rgb, strength=.28):
    w = bpy.context.scene.world
    w.use_nodes = True
    bg = w.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (*rgb, 1)
    bg.inputs['Strength'].default_value = strength

def ground(mat, size=200):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0,0,-.02))
    o = bpy.context.object
    o.name = 'Ground'
    assign(o, mat)
    return o

def recorder(mats, prefix='Recorder'):
    body, dark, metal, screen, accent = mats
    cube(prefix+'_Body', (0,0,.48), (2.35,1.45,.48), body, .13)
    cube(prefix+'_TopPlate', (0,0,.735), (2.12,1.23,.06), metal, .05)
    cube(prefix+'_DisplayBezel', (-.43,.08,.785), (1.0,.68,.055), dark, .07)
    cube(prefix+'_Display', (-.43,.08,.817), (.84,.50,.018), screen, .025)
    # Screen bars and a recording indicator.
    cube(prefix+'_Waveform', (-.48,.08,.831), (.52,.045,.009), accent, .009)
    cube(prefix+'_Timeline', (-.48,-.08,.831), (.60,.018,.009), accent, .004)
    sphere(prefix+'_RecordLED', (-.08,-.03,.83), (.035,.035,.018), accent, 16, 8)
    # Speaker grille: a compact double row of apertures.
    for row in range(3):
        for col in range(8):
            x = .29 + col*.105
            y = .36 - row*.13
            cyl(f'{prefix}_Grille_{row}_{col}', (x,y,.785), .026, .014, dark, 20, .003)
    # Controls and connector ports.
    cyl(prefix+'_ControlWheel', (.76,-.37,.80), .22, .09, dark, 64, .02)
    torus(prefix+'_WheelRim', (.76,-.37,.852), .175, .018, accent)
    for i, x in enumerate((-.88,-.52,-.16)):
        cyl(f'{prefix}_Button_{i}', (x,-.48,.79), .075, .07, accent if i==0 else dark, 32, .012)
    for i in range(3):
        cyl(f'{prefix}_Port_{i}', (-.76+i*.32,.736,.46), .07, .02, dark, 32, .008, (0,1,0))

def uv_unwrap():
    for o in [x for x in bpy.context.scene.objects if x.type == 'MESH']:
        try:
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(island_margin=.025)
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except Exception: pass

def geometry_stats():
    deps = bpy.context.evaluated_depsgraph_get()
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.hide_render]
    verts = faces = tris = 0
    for o in objects:
        e = o.evaluated_get(deps)
        m = e.to_mesh()
        m.calc_loop_triangles()
        verts += len(m.vertices); faces += len(m.polygons); tris += len(m.loop_triangles)
        e.to_mesh_clear()
    return {'mesh_objects': len(objects), 'evaluated_vertices': verts, 'evaluated_faces': faces, 'evaluated_triangles': tris}

def save_and_render(folder, base, extra_images=None):
    folder.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = RES
    scene.cycles.samples = 20
    uv_unwrap()
    metrics = {'project': base, 'blender_version': bpy.app.version_string, 'resolution': list(RES), 'render_engine': 'Cycles CPU', 'samples': scene.cycles.samples, **geometry_stats(), 'renders': []}
    if extra_images:
        render_specs = extra_images
    else:
        render_specs = [('beauty.png', None)]
    for filename, toggle in render_specs:
        if toggle: toggle()
        scene.render.filepath = str(folder / filename)
        t0 = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        elapsed = round(time.perf_counter()-t0, 2)
        metrics['renders'].append({'file': filename, 'render_seconds': elapsed})
    if extra_images and extra_images[0][1]: extra_images[0][1]()
    scene.render.filepath = str(folder / (render_specs[0][0] if render_specs else 'beauty.png'))
    blend_path = folder / f'{base}.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    metrics['blend_file'] = blend_path.name
    with open(folder/'metrics.json','w',encoding='utf-8') as f: json.dump(metrics,f,indent=2)
    print('PROJECT_METRICS', json.dumps(metrics))

def project1():
    folder = ROOT/'01_portable_audio_recorder'
    s = reset_scene('01 Portable Audio Recorder — Product Hero')
    body=material('Graphite anodized aluminum',(0.075,.105,.13),.72,.28)
    dark=material('Control black polymer',(.012,.022,.03),.15,.28)
    metal=material('Brushed titanium',(.3,.39,.44),.78,.24)
    screen=material('Display glass',(.01,.12,.17),.12,.18,(.01,.3,.42),.5)
    accent=material('Signal teal',(.01,.52,.39),.25,.25,(.02,.75,.48),1.2)
    floor=material('Studio floor',(.035,.05,.065),.12,.36)
    recorder((body,dark,metal,screen,accent))
    ground(floor)
    camera((3.5,-5.1,3.5),(0,0,.48),58)
    world_color((.055,.075,.095),.32)
    area('Key softbox',(-3,-4,5),(0,0,.4),520,(.78,.89,1),4)
    area('Warm rim',(3,2,4),(0,0,.45),680,(1,.61,.34),3)
    area('Front fill',(1,-4,2.5),(0,0,.5),260,(.36,.75,1),3)
    save_and_render(folder,'portable_audio_recorder')

def project2():
    folder = ROOT/'02_modular_utility_panel'
    s = reset_scene('02 Modular Sci-Fi Utility Panel — Asset Kit')
    base=material('Deep navy structure',(.025,.055,.085),.65,.32)
    panel=material('Blue steel panels',(.09,.19,.26),.7,.29)
    panel2=material('Secondary panels',(.14,.23,.27),.55,.32)
    trim=material('Titanium trim',(.48,.56,.59),.8,.22)
    dark=material('Vent recess',(.008,.016,.023),.28,.25)
    amber=material('Status amber',(.75,.26,.045),.25,.25,(.9,.14,.015),.7)
    floor=material('Studio floor',(.025,.038,.052),.12,.42)
    cube('Kit_Backplate',(0,0,.12),(4.4,2.45,.28),base,.12)
    for r in range(2):
        for c in range(3):
            x=(c-1)*1.34; y=(r-.5)*1.15
            cube(f'Module_{r}_{c}',(x,y,.34),(1.22,1.02,.19),panel if (r+c)%2==0 else panel2,.08)
            cube(f'Inset_{r}_{c}',(x,y,.445),(.77,.58,.035),dark,.035)
            for k in range(5):
                cube(f'Vent_{r}_{c}_{k}',(x-.28+k*.14,y+.12,.47),(.055,.25,.035),trim,.012)
            cyl(f'LED_{r}_{c}',(x+.38,y-.3,.47),.042,.025,amber,24,.005)
            for dx in (-.48,.48):
                for dy in (-.38,.38):
                    cyl(f'Fastener_{r}_{c}_{dx}_{dy}',(x+dx,y+dy,.47),.032,.025,trim,24,.004)
    ground(floor,100)
    camera((4.5,-6.7,4.1),(0,0,.24),54)
    world_color((.035,.06,.09),.34)
    area('Key',( -3,-4,6),(0,0,.2),700,(.63,.83,1),4)
    area('Rim',(3,3,4),(0,0,.2),900,(.22,.65,1),3)
    area('Warm fill',(4,-2,2),(0,0,.2),240,(1,.42,.16),3)
    save_and_render(folder,'modular_utility_panel')

def leaf(name, loc, scale, rot, mat):
    o=sphere(name,loc,scale,mat,24,16)
    o.rotation_euler=rot
    return o

def project3():
    folder = ROOT/'03_stylized_desk_plant'
    s = reset_scene('03 Stylized Desk Plant — Organic Study')
    pot=material('Terracotta ceramic',(.54,.16,.09),.05,.28)
    rim=material('Warm ceramic glaze',(.78,.33,.16),.08,.22)
    soil=material('Soil',(.055,.03,.018),0,.95)
    leafmats=[material('Leaf deep green',(.035,.22,.11),.05,.38),material('Leaf jade',(.08,.42,.21),.03,.32),material('Leaf lime accent',(.25,.54,.18),.02,.36)]
    stemmat=material('Stem green',(.08,.28,.1),0,.55)
    floor=material('Backdrop',(.045,.08,.07),.08,.55)
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=.48, radius2=.64, depth=.82, location=(0,0,.41))
    o=bpy.context.object; o.name='Planter_Tapered_Pot'; assign(o,pot); bevel(o,.045,3)
    bpy.ops.mesh.primitive_torus_add(major_radius=.61,minor_radius=.055,major_segments=64,minor_segments=12,location=(0,0,.82))
    assign(bpy.context.object,rim); bpy.context.object.name='Planter_Rim'
    cyl('Soil_Surface',(0,0,.82),.56,.035,soil,64,.008)
    # Four branching stems and paired elongated leaves, composed as editable meshes.
    for stem_i, angle in enumerate((0,math.pi/2,math.pi,3*math.pi/2)):
        dx,dy=math.cos(angle),math.sin(angle)
        start=Vector((dx*.08,dy*.08,.83)); end=Vector((dx*.18,dy*.18,2.0+(stem_i%2)*.25))
        bpy.ops.curve.primitive_bezier_curve_add(location=(0,0,0))
        st=bpy.context.object; st.name=f'Stem_{stem_i}'; st.data.dimensions='3D'; st.data.bevel_depth=.022; st.data.bevel_resolution=3
        sp=st.data.splines[0]; sp.bezier_points[0].co=start; sp.bezier_points[0].handle_left_type='AUTO'; sp.bezier_points[0].handle_right_type='AUTO'; sp.bezier_points[1].co=end; sp.bezier_points[1].handle_left_type='AUTO'; sp.bezier_points[1].handle_right_type='AUTO'; assign(st,stemmat)
        for j,t in enumerate((.38,.58,.76,.9)):
            center=start.lerp(end,t)
            for side in (-1,1):
                direction=Vector((dx*.35+(-dy)*side*.5,dy*.35+dx*side*.5,.38+(.04*j)))
                pos=center+direction*.28
                leaf(f'Leaf_{stem_i}_{j}_{side}',pos,(.18,.055,.39 if j<3 else .31),(direction.y*.7,-direction.x*.7,angle+side*.34),leafmats[(stem_i+j+side)%3])
    ground(floor,100)
    camera((3.8,-5.6,3.35),(0,0,1.1),58)
    world_color((.06,.095,.08),.32)
    area('Key',(-3,-4,5),(0,0,1),620,(1,.78,.53),3.6)
    area('Green rim',(3,2,4),(0,0,1),720,(.36,1,.56),3)
    area('Fill',(2,-4,2.5),(0,0,1),260,(.55,.8,1),3)
    save_and_render(folder,'stylized_desk_plant')

def project4():
    folder = ROOT/'04_lighting_study'
    s = reset_scene('04 Three-Point Lighting Study — One Object Three Moods')
    body=material('Neutral satin product',(.23,.31,.36),.48,.27)
    dark=material('Control material',(.025,.038,.046),.1,.24)
    screen=material('Screen',(.02,.16,.2),.18,.18,(.01,.16,.23),.25)
    accent=material('Indicator',(.1,.7,.5),.2,.22,(.05,.6,.4),.6)
    floor=material('Neutral ground',(.055,.065,.075),.05,.42)
    recorder((body,dark,body,screen,accent),'Study_Product')
    ground(floor)
    camera((3.7,-5.3,3.35),(0,0,.48),58)
    world_color((.075,.09,.11),.32)
    soft=[area('Soft_Key',(-3,-4,5),(0,0,.45),520,(1,.88,.74),4),area('Soft_Fill',(1,-4,3),(0,0,.45),260,(.65,.82,1),3),area('Soft_Rim',(3,2,4),(0,0,.45),600,(.9,.95,1),3)]
    dramatic=[area('Dramatic_Key',(-3,-2,5),(0,0,.45),800,(1,.55,.28),1.3,'SQUARE'),area('Dramatic_Rim',(2,3,3),(0,0,.45),850,(.08,.42,1),1.0,'SQUARE'),area('Dramatic_Fill',(0,-4,1.8),(0,0,.45),80,(.2,.35,.55),2)]
    cool=[area('Cool_Key',(-3,-3,5),(0,0,.45),600,(.34,.72,1),2.4),area('Cool_Fill',(2,-4,2.8),(0,0,.45),260,(.35,.92,1),3),area('Cool_Rim',(2,2,4),(0,0,.45),700,(.12,.55,1),2)]
    setups=[('beauty_soft.png',soft),('beauty_dramatic.png',dramatic),('beauty_cool.png',cool)]
    # Save with the studio set active; render each lighting variation in sequence.
    for group in setups:
        for light in group[1]: light.hide_render = (group[1] is not soft)
    specs=[]
    for filename,active in setups:
        def activate(active=active):
            for group in setups:
                for light in group[1]: light.hide_render = (group[1] is not active)
        specs.append((filename,activate))
    save_and_render(folder,'three_point_lighting_study',specs)

def curve_cable(name, points, mat, radius=.04, node_group=None):
    cdata=bpy.data.curves.new(name+'_Path','CURVE'); cdata.dimensions='3D'; cdata.resolution_u=24
    spline=cdata.splines.new('BEZIER'); spline.bezier_points.add(len(points)-1)
    for bp,pt in zip(spline.bezier_points,points): bp.co=pt; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,cdata); bpy.context.collection.objects.link(obj); assign(obj,mat)
    if node_group:
        mod=obj.modifiers.new('Procedural cable profile','NODES'); mod.node_group=node_group
    else:
        cdata.bevel_depth=radius; cdata.bevel_resolution=5; cdata.resolution_u=32
    return obj

def cable_nodes():
    group=bpy.data.node_groups.new('Cable_Profile_Curve_to_Mesh','GeometryNodeTree')
    group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    nodes=group.nodes; links=group.links
    inp=nodes.new('NodeGroupInput'); inp.location=(-400,80)
    circle=nodes.new('GeometryNodeCurvePrimitiveCircle'); circle.location=(-400,-130)
    circle.inputs['Resolution'].default_value=10; circle.inputs['Radius'].default_value=.045
    c2m=nodes.new('GeometryNodeCurveToMesh'); c2m.location=(-120,80)
    out=nodes.new('NodeGroupOutput'); out.location=(130,80)
    links.new(inp.outputs['Geometry'],c2m.inputs['Curve']); links.new(circle.outputs['Curve'],c2m.inputs['Profile Curve']); links.new(c2m.outputs['Mesh'],out.inputs['Geometry'])
    return group

def project5():
    folder = ROOT/'05_procedural_cable_kit'
    s = reset_scene('05 Procedural Cable and Connector Kit')
    cablemat=material('Cable jacket',(.045,.12,.19),.24,.31)
    cablemat2=material('Accent cable',(.04,.44,.36),.18,.3)
    metal=material('Connector titanium',(.42,.51,.56),.82,.2)
    black=material('Connector polymer',(.018,.025,.03),.08,.3)
    glow=material('Connector status light',(.08,.65,.46),.15,.23,(.025,.6,.33),.9)
    floor=material('Backdrop',(.027,.045,.057),.08,.42)
    ng=cable_nodes()
    paths=[ [(-2.0,-.45,.3),(-1.2,-.45,.75),(0,-.45,.55),(1.1,-.45,.34),(2.0,-.45,.52)],
            [(-2.0,.65,.3),(-1.15,.65,.5),(-.1,.65,.85),(1.1,.65,.52),(2.0,.65,.3)] ]
    for i,pts in enumerate(paths):
        curve_cable(f'Cable_{i+1}',pts,cablemat if i==0 else cablemat2,.04,ng)
        for end,pt in enumerate((Vector(pts[0]),Vector(pts[-1]))):
            tangent=Vector(pts[1])-Vector(pts[0]) if end==0 else Vector(pts[-1])-Vector(pts[-2])
            cyl(f'Connector_{i+1}_{end}_Housing',pt,.16,.35,black,48,.025,tangent)
            cyl(f'Connector_{i+1}_{end}_MetalSleeve',pt+tangent.normalized()*.13,.135,.13,metal,48,.018,tangent)
            cyl(f'Connector_{i+1}_{end}_Tip',pt+tangent.normalized()*.24,.085,.07,glow if i==0 else metal,40,.012,tangent)
            for ring in (-.1,-.02): torus(f'Connector_{i+1}_{end}_Ridge_{ring}',pt+tangent.normalized()*ring,.148,.015,metal,tangent)
    # End-point test connectors and assembly are intentionally visible in camera view.
    ground(floor,100)
    camera((4.1,-6.2,4.0),(0,0,.44),52)
    world_color((.035,.065,.09),.3)
    area('Key',(-3,-4,5),(0,0,.4),600,(.67,.85,1),4)
    area('Rim',(3,3,4),(0,0,.4),780,(.1,.8,.68),3)
    area('Warm fill',(4,-2,2.2),(0,0,.4),230,(1,.42,.18),3)
    save_and_render(folder,'procedural_cable_connector_kit')

project1(); project2(); project3(); project4(); project5()
print('ALL_PROJECTS_COMPLETE', str(ROOT))
