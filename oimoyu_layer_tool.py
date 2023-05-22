import bpy
import math
from mathutils import Vector, Matrix
from math import radians
from mathutils import Matrix, Vector
import math
import re
import numpy as np
import mathutils


class Layer:
    def __init__(self):
        mix_node = None
        pass
        

class LayerGroup:
    def __init__(self,layer_list):
        layer_num = None
        pass


def generate_layer_node(context):
    selected_obj_list = bpy.context.selected_objects

    settings = context.scene.oimoyu_layer_tool_settings
    layer_num = settings.layer_num
    is_mix_shader = settings.is_mix_shader
    is_wrap = settings.is_wrap
    
    if selected_obj_list:
        obj = selected_obj_list[0]
    else:
        ShowMessageBox('No Object Selected!')
        return
    
    # deselect all node
    node_tree = bpy.context.space_data.node_tree
    for node in node_tree.nodes:
        node.select = False
        
        
    mat = bpy.context.object.active_material
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    frame_node = nodes.new(type="NodeFrame")
    frame_node.location = (0,0)
    
    # create reroute node
    reroute_node_list = []
    for i in range(layer_num):
        # create reroute 
        reroute_node_color = mat.node_tree.nodes.new('NodeReroute')
        reroute_node_color.location = (-150, -i*200 - 50)
        reroute_node_color.parent = frame_node
        reroute_node_alpha = mat.node_tree.nodes.new('NodeReroute')
        reroute_node_alpha.location = (-150, -i*200 - 70)
        reroute_node_alpha.parent = frame_node
        reroute_node_list.append({'color': reroute_node_color, 'alpha': reroute_node_alpha})
        
    reroute_node_output = mat.node_tree.nodes.new('NodeReroute')
    reroute_node_output.location = ((layer_num)*200, -layer_num*150/2)
    reroute_node_output.parent = frame_node
    
    # create maximum node
    maximum_node_list = []
    for i in range(layer_num):
        if i == layer_num-1:
            continue
        maximum_node = mat.node_tree.nodes.new('ShaderNodeMath')
        maximum_node.operation = 'MAXIMUM'
        maximum_node.inputs[0].default_value = 1
        maximum_node.inputs[1].default_value = 0
        maximum_node.location = (200*i, -(i+1)*200)
        maximum_node.parent = frame_node
        maximum_node_list.append(maximum_node)
    
    transparent_node = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    transparent_node.location = (200*(layer_num-2), -(layer_num)*200)
    transparent_node.parent = frame_node


    # create mix node
    mix_node_list = []
    for i in range(layer_num):
        if is_mix_shader:
            mix_node = mat.node_tree.nodes.new('ShaderNodeMixShader')
        elif i != layer_num -1:
            mix_node = mat.node_tree.nodes.new('ShaderNodeMixRGB')
#            mix_node.inputs[0].default_value = 0
        else:
            mix_node = mat.node_tree.nodes.new('ShaderNodeMixShader')
#            mix_node.inputs[0].default_value = 1

        mix_node.inputs[0].default_value = 1
        
        mix_node.location = (200*i, -i*150)
        mix_node.parent = frame_node
        mix_node_list.append(mix_node)
        
        if i != layer_num-1:
            mix_node.label = f"Mix_{layer_num-i-1}"

    
#    # connect node
    if layer_num >1:
        mat.node_tree.links.new(reroute_node_list[0]['alpha'].outputs[0], maximum_node_list[0].inputs[0])
        mat.node_tree.links.new(mix_node_list[-2].outputs[0], mix_node_list[-1].inputs[2])
        mat.node_tree.links.new(maximum_node_list[-1].outputs[0], mix_node_list[-1].inputs[0])
        mat.node_tree.links.new(mix_node_list[-2].outputs[0], mix_node_list[-1].inputs[2])
    else:
        mat.node_tree.links.new(reroute_node_list[0]['color'].outputs[0], mix_node_list[0].inputs[2])
        mat.node_tree.links.new(reroute_node_list[0]['alpha'].outputs[0], mix_node_list[0].inputs[0])
        
    mat.node_tree.links.new(reroute_node_list[0]['color'].outputs[0], mix_node_list[0].inputs[1])
    mat.node_tree.links.new(transparent_node.outputs[0], mix_node_list[-1].inputs[1])
    mat.node_tree.links.new(mix_node_list[-1].outputs[0], reroute_node_output.inputs[0])
    
    for i in range(layer_num):
            
        if i != layer_num - 2 and i != layer_num - 1:
            mat.node_tree.links.new(maximum_node_list[i].outputs[0], maximum_node_list[i+1].inputs[0])
            mat.node_tree.links.new(mix_node_list[i].outputs[0], mix_node_list[i+1].inputs[1])
            
        if i != 0:
            mat.node_tree.links.new(reroute_node_list[i]['color'].outputs[0], mix_node_list[i-1].inputs[2])
            mat.node_tree.links.new(reroute_node_list[i]['alpha'].outputs[0], mix_node_list[i-1].inputs[0])
            mat.node_tree.links.new(reroute_node_list[i]['alpha'].outputs[0], maximum_node_list[i-1].inputs[1])

    if not is_mix_shader:
        # create preprocess node
        # create preprocess reroute node
        prep_reroute_node_list = []
        for i in range(layer_num):
            # create reroute 
            reroute_node_color = mat.node_tree.nodes.new('NodeReroute')
            reroute_node_color.location = (-800, -i*200 - 50)
            reroute_node_color.parent = frame_node
            reroute_node_alpha = mat.node_tree.nodes.new('NodeReroute')
            reroute_node_alpha.location = (-800, -i*200 - 70)
            reroute_node_alpha.parent = frame_node
            prep_reroute_node_list.append({'color': reroute_node_color, 'alpha': reroute_node_alpha})
        
        # create preprocess math node
        prep_math_node_list = []
        for i in range(layer_num):
            temp_list = []
            math_node_1 = mat.node_tree.nodes.new('ShaderNodeMath')
            math_node_1.operation = 'LESS_THAN'
            math_node_1.parent = frame_node
            math_node_1.inputs[0].default_value = 3
            math_node_1.inputs[1].default_value = 2
            math_node_1.location = (-600, -(i)*400)
            temp_list.append(math_node_1)
            
            math_node_2 = mat.node_tree.nodes.new('ShaderNodeMath')
            math_node_2.operation = 'MULTIPLY'
            math_node_2.parent = frame_node
            math_node_2.inputs[0].default_value = 1
            math_node_2.inputs[1].default_value = 1
            math_node_2.location = (-600, -(i)*400-200)
            temp_list.append(math_node_2)
            
            math_node_3 = mat.node_tree.nodes.new('ShaderNodeMath')
            math_node_3.operation = 'MULTIPLY'
            math_node_3.parent = frame_node
        #    math_node_1.inputs[0].default_value = 0
            math_node_3.location = (-400, -(i)*200)
            temp_list.append(math_node_3)

            prep_math_node_list.append(temp_list)


        # connect preprocess math node
        for i in range(layer_num):
            mat.node_tree.links.new(prep_math_node_list[i][0].outputs[0], prep_math_node_list[i][2].inputs[0])
            mat.node_tree.links.new(prep_math_node_list[i][1].outputs[0], prep_math_node_list[i][2].inputs[1])
            mat.node_tree.links.new(prep_math_node_list[i][2].outputs[0],reroute_node_list[i]['alpha'].inputs[0])
            mat.node_tree.links.new(prep_reroute_node_list[i]['color'].outputs[0],reroute_node_list[i]['color'].inputs[0])
            mat.node_tree.links.new(prep_reroute_node_list[i]['color'].outputs[0],prep_math_node_list[i][0].inputs[0])
            mat.node_tree.links.new(prep_reroute_node_list[i]['alpha'].outputs[0],prep_math_node_list[i][1].inputs[0])
        
        
        # process for mix shader
        if is_mix_shader:
            for i in range(layer_num):
                from_node = prep_reroute_node_list[i]['color']
                to_node = prep_math_node_list[i][0]
                
                new_node = mat.node_tree.nodes.new(type='ShaderNodeShaderToRGB')
                new_node.parent = frame_node
                new_node.location = ((from_node.location.x + to_node.location.x) / 2, 
                                    (from_node.location.y + to_node.location.y) / 2)
                mat.node_tree.links.new(from_node.outputs[0], new_node.inputs[0])
                mat.node_tree.links.new(new_node.outputs[0], to_node.inputs[0])
                
                if is_wrap:
                    new_node.location = (0,0)

    if is_wrap:
        for i in [maximum_node_list]:
            for node in i:
                node.location = (0, 0)

        transparent_node.location = (0, 0)
        reroute_node_output.location = (200, -200)
        
        if not is_mix_shader:
            for i in prep_math_node_list:
                for node in i:
                    node.location = (0, 0)
            idx = -1
            for i in prep_reroute_node_list:
                idx += 1
                i['color'].location.x += 600
                i['alpha'].location.x += 600
                
                i['color'].location.y += 40 * idx
                i['alpha'].location.y += 40 * idx
                
            for i in reroute_node_list:
                i['color'].location = (0, 0)
                i['alpha'].location = (0, 0)
        
        if is_mix_shader:
            for i in mix_node_list:
                i.location = (0, 0)
        else:
            idx=-1
            for i in mix_node_list[:-1]:
                idx+=1
                i.location.x = -150
                i.location.y -= 25 * idx + 100
            mix_node_list[-1].location = (0, 0)
    
    # create texture node
    if not is_mix_shader:
        for i in range(layer_num):
            texture_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            texture_node.location = prep_reroute_node_list[i]['color'].location
            texture_node.location.x -= 300
            texture_node.location.y += 50 - i * 100
            
            mat.node_tree.links.new(texture_node.outputs[0], prep_reroute_node_list[i]['color'].inputs[0])
            mat.node_tree.links.new(texture_node.outputs[1], prep_reroute_node_list[i]['alpha'].inputs[0])
            

def remove_image(image_name):

    # Find the image by name
    image = bpy.data.images.get(image_name)
    
    # check image
    if image is not None:
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image == image:
#                        node.image = None
                        return {'result': False, 'msg': f'material name:{material.name}'}
                    
        # Unlink and remove the image
        bpy.data.images.remove(image)
        
    return True


def combine_image(context):
    settings = context.scene.oimoyu_layer_tool_settings
    image_list = settings.my_image_list
    if len(image_list) < 2:
        ShowMessageBox('At least two image in list')
        return
    image_name_list = [temp.name for temp in image_list]
    
    def check_same_shape(images):
        # Get the shape (width, height) of the first image
        first_image_shape = (images[0].size[0], images[0].size[1])

        # Iterate over the remaining images and compare their shape with the first image
        for image in images[1:]:
            image_shape = (image.size[0], image.size[1])

            if image_shape != first_image_shape:
                return False

        return True

    def blend_image_alpha(image_list):
        previous_pixels = []
        for i in range(len(image_list)-1):
            if previous_pixels:
                pixels1 = previous_pixels
                pixels2 = list(image_list[i+1].pixels)
            else:
                pixels1 = list(image_list[i].pixels)
                pixels2 = list(image_list[i+1].pixels)

            # Combine images
            output_pixels = []
            for i in range(0, len(pixels1), 4):
                r1, g1, b1, a1 = pixels1[i:i+4]
                r2, g2, b2, a2 = pixels2[i:i+4]
                
                # Alpha blending
                a = a1 + a2 * (1 - a1)
                if a != 0:  # To avoid division by zero
                    r = (r1 * a1 + r2 * a2 * (1 - a1)) / a
                    g = (g1 * a1 + g2 * a2 * (1 - a1)) / a
                    b = (b1 * a1 + b2 * a2 * (1 - a1)) / a
                else:
                    r = g = b = 0

                output_pixels.extend([r, g, b, a])
            previous_pixels = output_pixels
        return previous_pixels
        
    image_list = [bpy.data.images[temp] for temp in image_name_list]

    assert check_same_shape(image_list), "Images must be the same size"
    
    width = image_list[0].size[0]
    height = image_list[0].size[1]
    
    result_pixels = blend_image_alpha(image_list)
    
    output_image_name = "Oimoyu_Layertool_Combined_Image"
    image_temp = bpy.data.images.get(output_image_name)
    if image_temp:
        bpy.data.images.remove(image_temp)
    
    output_image = bpy.data.images.new(output_image_name, width=width, height=height)
    output_image.pixels = result_pixels
    
    context.scene.oimoyu_layer_tool_settings.my_image_list.clear()
    
    

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
        
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
    
bl_info = {
    "name": "Layer Tool",
    "author": "Oimoyu",
    "version": (1, 0),
    "blender": (3, 3, 6),
    "location": "ShaderEditor > Sidebar > Oimoyu Layer Tool",
    "description": "Generate Layer Shader Node",
    "category": "Shader",
}







class MY_UL_CombineImageList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name, icon_value=layout.icon(item))
        
class MoveCombineImage(bpy.types.Operator):
    bl_idname = "oimoyu_layertool.move_combine_image"
    bl_label = ""
#    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        scn = context.scene
        return scn.oimoyu_layer_tool_settings.my_image_list_index < len(scn.oimoyu_layer_tool_settings.my_image_list)

    def execute(self, context):
        scn = context.scene
        idx = scn.oimoyu_layer_tool_settings.my_image_list_index

        try:
            if self.direction == 'UP':
                scn.oimoyu_layer_tool_settings.my_image_list.move(idx, idx-1)
            elif self.direction == 'DOWN':
                scn.oimoyu_layer_tool_settings.my_image_list.move(idx, idx+1)
        except IndexError:
            pass

        return {'FINISHED'}

class AddCombineImage(bpy.types.Operator):
    bl_idname = "oimoyu_layertool.add_combine_image"
    bl_label = "Add Image to List"
#    bl_options = {'REGISTER', 'UNDO'}

    image_name: bpy.props.StringProperty()

    def execute(self, context):
        scn = context.scene
        
        mat = bpy.context.object.active_material
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        images = []
        if mat and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    images.append(node.image)
        images = images[::-1]
        for image in images:
            if image:
                scn.oimoyu_layer_tool_settings.my_image_list.add().name = image.name
   
        return {'FINISHED'}

class DeleteCombineImage(bpy.types.Operator):
    bl_idname = "oimoyu_layertool.delete_combine_image"
    bl_label = "Delete Image from List"
#    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scn = context.scene
        return scn.oimoyu_layer_tool_settings.my_image_list_index < len(scn.oimoyu_layer_tool_settings.my_image_list)

    def execute(self, context):
        scn = context.scene
        idx = scn.oimoyu_layer_tool_settings.my_image_list_index
        scn.oimoyu_layer_tool_settings.my_image_list.remove(idx)
        return {'FINISHED'}
    
    
class CombineImageOperator(bpy.types.Operator):
    bl_idname = "oimoyu_layertool.combine_image"
    bl_label = "Combine image"

    def execute(self, context):
        combine_image(context)
        return {'FINISHED'}
    
    
    
    
    
class SwitchEraserOperator(bpy.types.Operator):
    bl_idname = "oimoyu_layer_tool.switch_eraser"
    bl_label = ""

    def execute(self, context):
        bpy.context.tool_settings.image_paint.brush = bpy.data.brushes['Draw']
        bpy.context.tool_settings.image_paint.brush.blend = 'ERASE_ALPHA'
        return {'FINISHED'}
    
class SwitchBrushOperator(bpy.types.Operator):
    bl_idname = "oimoyu_layer_tool.switch_brush"
    bl_label = ""

    def execute(self, context):
        bpy.context.tool_settings.image_paint.brush = bpy.data.brushes['Draw']
        bpy.context.tool_settings.image_paint.brush.blend = 'MIX'
        return {'FINISHED'}


def toggle_hotkey(self, context):
    settings = context.scene.oimoyu_layer_tool_settings
    if settings.enable_hotkey:
        register_hotkey()
    else:
        unregister_hotkey()
    
class LayerToolSettings(bpy.types.PropertyGroup):
    layer_num : bpy.props.IntProperty(name="Layer Number",min=1,default=1)
    is_mix_shader : bpy.props.BoolProperty(name="Is Mix Shader",description="Enable Angle Limit",default=False)
    is_wrap : bpy.props.BoolProperty(name="Is Wrap Shader",description="Wrap All Shader",default=True)
    
    my_image_list : bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    my_image_list_index : bpy.props.IntProperty()

    enable_hotkey : bpy.props.BoolProperty(name="Enable Hotkey",description="Enable Hotkey",default=True, update=toggle_hotkey)
    

class GenerateLayerNodeOperator(bpy.types.Operator):
    bl_idname = "oimoyu_layertool.generate_layer_node"
    bl_label = "Generate Layer Node"

    def execute(self, context):
        generate_layer_node(context)
        return {'FINISHED'}
    

class MainPanel(bpy.types.Panel):
    bl_label = "Layer Tool"
    bl_idname = "VIEW3D_PT_OIMOYU_LAYER_TOOL"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Oimoyu Layer Tool"
    
    def draw(self, context):
        settings = context.scene.oimoyu_layer_tool_settings
        
        self.layout.prop(settings, "enable_hotkey")
        
        selected_obj_list = bpy.context.selected_objects
        if selected_obj_list:
            selected_object = selected_obj_list[0]
            self.layout.label(text="Selected Object: " + selected_object.name)
            
            mat = bpy.context.object.active_material
            if mat:
                self.layout.label(text="Active Material: " + mat.name)

                row = self.layout.row()
                row.label(text="Layer num")
                row.prop(settings, "layer_num", text="")
            
                self.layout.prop(settings, "is_mix_shader")
                self.layout.prop(settings, "is_wrap")
                
                self.layout.operator("oimoyu_layertool.generate_layer_node", text="Generate Layer Node")
            else:
                self.layout.label(text="No Material active")

        else:
            self.layout.label(text="No objects selected")
            
        
        self.layout.separator()
        self.layout.separator()
        self.layout.separator()
        self.layout.separator()
        self.layout.label(text="Combine Image")
        self.layout.template_list("MY_UL_CombineImageList", "", context.scene.oimoyu_layer_tool_settings, "my_image_list", context.scene.oimoyu_layer_tool_settings, "my_image_list_index")
        row = self.layout.row(align=True)
        row.operator("oimoyu_layertool.move_combine_image", text='Up').direction = 'UP'
        row.operator("oimoyu_layertool.move_combine_image", text='Down').direction = 'DOWN'
        row.operator("oimoyu_layertool.add_combine_image", text='Add')
        row.operator("oimoyu_layertool.delete_combine_image", text='Delete')
        if settings.my_image_list:
            self.layout.operator("oimoyu_layertool.combine_image", text="Combine Image")
        
        
classes = (
    MainPanel,
    GenerateLayerNodeOperator,
    MY_UL_CombineImageList,
    MoveCombineImage,
    AddCombineImage,
    DeleteCombineImage,
    CombineImageOperator,
    SwitchEraserOperator,
    SwitchBrushOperator
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.utils.register_class(LayerToolSettings)
    bpy.types.Scene.oimoyu_layer_tool_settings = bpy.props.PointerProperty(type=LayerToolSettings)
    register_hotkey()
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(LayerToolSettings)
    del bpy.types.Scene.oimoyu_layer_tool_settings
    unregister_hotkey()
    

addon_keymaps = []
def register_hotkey():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
        kmi = km.keymap_items.new(SwitchEraserOperator.bl_idname, 'E', 'PRESS', ctrl=False, shift=False)
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
        kmi = km.keymap_items.new(SwitchBrushOperator.bl_idname, 'B', 'PRESS', ctrl=False, shift=False)
        addon_keymaps.append((km, kmi))

def unregister_hotkey():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()