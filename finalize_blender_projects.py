import bpy
from pathlib import Path

ROOT=Path(__file__).resolve().parent/'3d_projects'
for blend in ROOT.rglob('*.blend'):
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    scene.unit_settings.scale_length=1.0
    scene['Portfolio status']='Assistant-generated Blender prototype created at the user\'s request; candidate should review and revise before claiming independent authorship.'
    scene['Blender version']=bpy.app.version_string
    collections={}
    for name in ('00_STAGE','01_ASSETS','02_LIGHTS','03_CAMERAS'):
        col=bpy.data.collections.get(name)
        if col is None:
            col=bpy.data.collections.new(name)
            scene.collection.children.link(col)
        collections[name]=col
    for obj in list(scene.objects):
        if obj.type=='LIGHT': target=collections['02_LIGHTS']
        elif obj.type=='CAMERA': target=collections['03_CAMERAS']
        elif obj.name=='Ground': target=collections['00_STAGE']
        else: target=collections['01_ASSETS']
        for col in list(obj.users_collection): col.objects.unlink(obj)
        target.objects.link(obj)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    print('FINALIZED',blend.name,scene.name)
print('ALL_PROJECTS_FINALIZED')
