
# Blender addon generate layer shader node

## Parameter Description

#### 
"Enable Hotkey": E -> erase alpha, B ->Brush

"Layer num": the Layer number for generate the shader node

"Is Mix Shader": if check,the input will be accept shader and color, if not, the input can only accept color.(checking this will be better performance, but less adaptive, every layer should have input to work)

"Is Wrap Shader": nodes will shrink together to save space


## How to use

* 1.Select object, create a material for that
* 2.Click the "Generate Layer Node" button, the node will be generated in current active material.
* 3.The node input is 1 to N layers from bottom to top. The first input of each layer is the color input and the second is the alpha input, and the node output is the shader.

demo video:https://www.bilibili.com/video/BV1Eg4y1c7BX/
